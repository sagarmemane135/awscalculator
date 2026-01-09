from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import httpx
from datetime import datetime, timedelta

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Using ec2instances.info API - a public, accurate, and fast pricing source
EC2_INSTANCES_API = "https://instances.vantage.sh/instances.json"

# Simple in-memory cache
_cache = {
    "data": None,
    "timestamp": None,
    "ttl": 3600  # Cache for 1 hour
}

# Clear cache function for debugging
def clear_cache():
    """Clear the pricing data cache"""
    _cache["data"] = None
    _cache["timestamp"] = None

@app.get("/")
def root():
    return {
        "message": "AWS EC2 Pricing API - No Authentication Required!",
        "endpoints": {
            "get_price": {
                "path": "/get-price",
                "description": "Get price for a specific instance type (supports On-Demand, Reserved, Spot)",
                "example": "/get-price?instance_type=t3.micro&region=us-east-1&pricing_type=reserved&ri_term=1yr&ri_payment=noUpfront&ri_type=Standard"
            },
            "search_instances": {
                "path": "/search",
                "description": "Search instances with filters",
                "example": "/search?min_vcpus=2&max_vcpus=4&min_memory=4&region=us-east-1"
            },
            "list_regions": {
                "path": "/regions",
                "description": "List all available AWS regions"
            },
            "list_families": {
                "path": "/families",
                "description": "List all instance families (t3, m5, etc.)"
            },
            "compare_instances": {
                "path": "/compare",
                "description": "Compare multiple instance types",
                "example": "/compare?instances=t3.micro,t3.small,t2.micro&region=us-east-1"
            },
            "cheapest": {
                "path": "/cheapest",
                "description": "Find cheapest instances matching criteria",
                "example": "/cheapest?min_vcpus=2&min_memory=4&region=us-east-1&limit=10"
            },
            "all_instances": {
                "path": "/instances",
                "description": "List all available instance types",
                "example": "/instances?region=us-east-1"
            },
            "get_price_value": {
                "path": "/get-price-value",
                "description": "Get only the price value (number only, no JSON) - supports all pricing types",
                "example": "/get-price-value?instance_type=t3.micro&region=us-east-1&pricing_type=spot&spot_type=avg"
            }
        },
        "data_source": "instances.vantage.sh (powered by ec2instances.info)"
    }

async def fetch_all_instance_data(force_refresh=False):
    """Fetch and cache all EC2 instance data"""
    
    # Force refresh if requested
    if force_refresh:
        _cache["data"] = None
        _cache["timestamp"] = None
    
    # Check if cache is valid
    if _cache["data"] and _cache["timestamp"]:
        age = (datetime.now() - _cache["timestamp"]).seconds
        if age < _cache["ttl"]:
            return _cache["data"]
    
    # Fetch fresh data
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(EC2_INSTANCES_API)
            if response.status_code == 200:
                data = response.json()
                _cache["data"] = data
                _cache["timestamp"] = datetime.now()
                return data
            return []
    except Exception as e:
        print(f"Error fetching instance data: {e}")
        # Return cached data even if expired, if available
        return _cache["data"] if _cache["data"] else []


def get_reserved_instance_price(os_pricing, ri_term=None, ri_payment=None, ri_type=None):
    """
    Extract Reserved Instance price based on term, payment, and type
    
    Parameters:
    - os_pricing: OS pricing dictionary
    - ri_term: '1yr' or '3yr' (optional)
    - ri_payment: 'allUpfront', 'partialUpfront', 'noUpfront' (optional)
    - ri_type: 'Standard', 'Convertible', 'Savings' (optional)
    
    Returns: price value or None
    """
    reserved = os_pricing.get('reserved', {})
    
    if not reserved:
        return None
    
    # If no specific parameters, return first available (backward compatibility)
    if not ri_term and not ri_payment and not ri_type:
        first_key = list(reserved.keys())[0] if reserved else None
        return reserved.get(first_key) if first_key else None
    
    # Build the key pattern
    term_map = {'1yr': 'yrTerm1', '3yr': 'yrTerm3'}
    term_prefix = term_map.get(ri_term, 'yrTerm1')
    
    type_map = {'Standard': 'Standard', 'Convertible': 'Convertible', 'Savings': 'Savings'}
    ri_type_name = type_map.get(ri_type, 'Standard')
    
    payment_map = {'allUpfront': 'allUpfront', 'partialUpfront': 'partialUpfront', 'noUpfront': 'noUpfront'}
    payment = payment_map.get(ri_payment, 'noUpfront')
    
    # Try to find exact match
    key = f"{term_prefix}{ri_type_name}.{payment}"
    if key in reserved:
        return reserved[key]
    
    # Try variations if exact match not found
    for k, v in reserved.items():
        if k.startswith(term_prefix) and ri_type_name in k and payment in k:
            return v
    
    # Fallback: return first matching term
    for k, v in reserved.items():
        if k.startswith(term_prefix):
            return v
    
    return None


def get_spot_instance_price(os_pricing, spot_type='avg'):
    """
    Extract Spot Instance price based on type
    
    Parameters:
    - os_pricing: OS pricing dictionary
    - spot_type: 'min', 'max', or 'avg' (default: 'avg')
    
    Returns: price value or None
    """
    spot_map = {
        'min': 'spot_min',
        'max': 'spot_max',
        'avg': 'spot_avg'
    }
    
    spot_key = spot_map.get(spot_type.lower(), 'spot_avg')
    price = os_pricing.get(spot_key)
    
    # Return the price even if it's 0 or empty string (but not None)
    if price is not None and price != '':
        return price
    return None


def get_pricing_details(os_pricing, pricing_type, ri_term=None, ri_payment=None, ri_type=None, spot_type='avg'):
    """
    Get pricing details with all options
    
    Returns: dict with price and additional info
    """
    # Debug: Check what we received
    if not os_pricing:
        print(f"get_pricing_details: os_pricing is empty or None")
        return None
    
    print(f"get_pricing_details: pricing_type={pricing_type}, os_pricing keys: {list(os_pricing.keys())[:10]}")
    
    if pricing_type.lower() == 'ondemand':
        price = os_pricing.get('ondemand')
        return {
            'price': float(price) if price else None,
            'pricing_info': {
                'type': 'On-Demand',
                'description': 'Pay-as-you-go pricing'
            }
        }
    
    elif pricing_type.lower() == 'reserved':
        price = get_reserved_instance_price(os_pricing, ri_term, ri_payment, ri_type)
        if price:
            return {
                'price': float(price),
                'pricing_info': {
                    'type': 'Reserved Instance',
                    'term': ri_term or '1yr',
                    'payment': ri_payment or 'noUpfront',
                    'ri_type': ri_type or 'Standard',
                    'description': f'{ri_type or "Standard"} RI - {ri_term or "1yr"} - {ri_payment or "noUpfront"}'
                },
                'all_ri_options': os_pricing.get('reserved', {})
            }
        return None
    
    elif pricing_type.lower() == 'spot':
        # Try to get spot price - check all possible keys
        spot_map = {
            'min': 'spot_min',
            'max': 'spot_max',
            'avg': 'spot_avg'
        }
        spot_key = spot_map.get(spot_type.lower(), 'spot_avg')
        
        # Direct check - if key exists, use it
        if spot_key in os_pricing:
            price = os_pricing[spot_key]
        else:
            price = os_pricing.get(spot_key)
        
        # If requested spot type not found, try to get any available spot price
        if not price or price == '':
            # Try spot_avg as fallback
            if 'spot_avg' in os_pricing:
                price = os_pricing['spot_avg']
                spot_type = 'avg'
            # If still None, try any spot key
            elif not price or price == '':
                for key in ['spot_avg', 'spot_min', 'spot_max']:
                    if key in os_pricing and os_pricing[key]:
                        price = os_pricing[key]
                        spot_type = 'avg' if key == 'spot_avg' else ('min' if key == 'spot_min' else 'max')
                        break
        
        # Also get all spot-related data
        spot_min = os_pricing.get('spot_min')
        spot_max = os_pricing.get('spot_max')
        spot_avg = os_pricing.get('spot_avg')
        pct_savings = os_pricing.get('pct_savings_od')
        pct_interrupt = os_pricing.get('pct_interrupt')
        
        # Check if we have any spot pricing data
        # Debug: print what we found
        print(f"Spot pricing check - price: {price}, type: {type(price)}, os_pricing keys: {list(os_pricing.keys())[:10]}")
        
        if price and price != '':
            try:
                # Convert to float - handle both string and numeric values
                price_float = float(price)
                return {
                    'price': price_float,
                    'pricing_info': {
                        'type': 'Spot Instance',
                        'spot_type': spot_type,
                        'description': f'Spot pricing ({spot_type})'
                    },
                    'spot_details': {
                        'min': float(spot_min) if spot_min and spot_min != '' else None,
                        'max': float(spot_max) if spot_max and spot_max != '' else None,
                        'avg': float(spot_avg) if spot_avg and spot_avg != '' else None,
                        'savings_vs_ondemand': float(pct_savings) if pct_savings and pct_savings != '' else None,
                        'interruption_rate': float(pct_interrupt) if pct_interrupt and pct_interrupt != '' else None
                    }
                }
            except (ValueError, TypeError) as e:
                print(f"Error converting spot price to float: {e}, price value: {price}")
                return None
        
        return None
    
    return None

@app.get("/get-price")
async def get_aws_price(
    instance_type: str,
    region: str = 'ap-south-1',
    os_type: str = 'linux',
    pricing_type: str = 'ondemand',
    ri_term: str = None,
    ri_payment: str = None,
    ri_type: str = None,
    spot_type: str = 'avg'
):
    """
    Get EC2 instance pricing with full support for Reserved Instances and Spot pricing
    
    Parameters:
    - instance_type: EC2 instance type (e.g., t3.micro)
    - region: AWS region code (e.g., ap-south-1, us-east-1)
    - os_type: Operating system (linux, windows, rhel, sles, mswinSQLWeb, mswinSQLStd)
    - pricing_type: ondemand, reserved, spot
    - ri_term: For Reserved Instances - '1yr' or '3yr' (optional)
    - ri_payment: For Reserved Instances - 'allUpfront', 'partialUpfront', 'noUpfront' (optional)
    - ri_type: For Reserved Instances - 'Standard', 'Convertible', 'Savings' (optional)
    - spot_type: For Spot Instances - 'min', 'max', or 'avg' (default: 'avg')
    """
    
    try:
        instances = await fetch_all_instance_data(force_refresh=(pricing_type.lower() == 'spot'))
        
        if not instances:
            raise HTTPException(status_code=503, detail="Unable to fetch pricing data")
        
        for instance in instances:
            try:
                if instance.get('instance_type') == instance_type:
                    pricing = instance.get('pricing', {})
                    
                    if not pricing:
                        continue
                    
                    region_data = pricing.get(region, {})
                    if not region_data:
                        return {
                            "error": f"Instance type '{instance_type}' not available in region '{region}'",
                            "instance_info": {
                                "type": instance_type,
                                "vcpus": instance.get('vCPU'),
                                "memory": instance.get('memory'),
                                "available_regions": list(pricing.keys()) if pricing else []
                            }
                        }
                    
                    os_pricing = region_data.get(os_type.lower(), {})
                    pricing_details = get_pricing_details(
                        os_pricing, 
                        pricing_type, 
                        ri_term, 
                        ri_payment, 
                        ri_type, 
                        spot_type
                    )
                    
                    if pricing_details and pricing_details.get('price') is not None:
                        response = {
                            "success": True,
                            "instance": instance_type,
                            "region": region,
                            "os": os_type,
                            "pricing_type": pricing_type,
                            "price": pricing_details['price'],
                            "currency": "USD",
                            "unit": "Hrs",
                            "pricing_info": pricing_details.get('pricing_info', {}),
                            "specs": {
                                "vcpus": instance.get('vCPU'),
                                "memory": instance.get('memory'),
                                "storage": instance.get('storage'),
                                "network": instance.get('network_performance'),
                                "family": instance.get('family'),
                                "processor": instance.get('physical_processor')
                            }
                        }
                        
                        # Add additional details for RI and Spot
                        if pricing_type.lower() == 'reserved' and 'all_ri_options' in pricing_details:
                            response['all_reserved_options'] = pricing_details['all_ri_options']
                        
                        if pricing_type.lower() == 'spot' and 'spot_details' in pricing_details:
                            response['spot_details'] = pricing_details['spot_details']
                        
                        return response
                    else:
                        # Instance found but pricing not available
                        error_msg = f"Pricing type '{pricing_type}' not available for instance '{instance_type}' in region '{region}'"
                        if pricing_type.lower() == 'spot':
                            error_msg += ". Spot pricing may not be available for this instance type."
                        elif pricing_type.lower() == 'reserved':
                            error_msg += ". Try different RI parameters (ri_term, ri_payment, ri_type)."
                        return {
                            "error": error_msg,
                            "hint": "Check if the instance supports this pricing model in this region"
                        }
            except Exception as e:
                print(f"Error processing instance {instance.get('instance_type', 'unknown')}: {e}")
                continue
        
        return {
            "error": f"Instance type '{instance_type}' not found",
            "hint": "Make sure the instance type name is correct (e.g., 't3.micro', not 't3micro')"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/get-price-value", response_class=PlainTextResponse)
async def get_aws_price_value(
    instance_type: str,
    region: str = 'ap-south-1',
    os_type: str = 'linux',
    pricing_type: str = 'ondemand',
    ri_term: str = None,
    ri_payment: str = None,
    ri_type: str = None,
    spot_type: str = 'avg'
):
    """
    Get only the price value as a number (no JSON, just the price)
    
    Returns: Just the price number (e.g., "0.0104")
    
    Parameters:
    - instance_type: EC2 instance type (e.g., t3.micro)
    - region: AWS region code (e.g., ap-south-1, us-east-1)
    - os_type: Operating system (linux, windows, rhel, sles)
    - pricing_type: ondemand, reserved, spot
    - ri_term: For Reserved Instances - '1yr' or '3yr' (optional)
    - ri_payment: For Reserved Instances - 'allUpfront', 'partialUpfront', 'noUpfront' (optional)
    - ri_type: For Reserved Instances - 'Standard', 'Convertible', 'Savings' (optional)
    - spot_type: For Spot Instances - 'min', 'max', or 'avg' (default: 'avg')
    """
    
    try:
        instances = await fetch_all_instance_data(force_refresh=(pricing_type.lower() == 'spot'))
        
        if not instances:
            raise HTTPException(status_code=503, detail="Unable to fetch pricing data")
        
        for instance in instances:
            try:
                if instance.get('instance_type') == instance_type:
                    pricing = instance.get('pricing', {})
                    
                    if not pricing:
                        continue
                    
                    region_data = pricing.get(region, {})
                    if not region_data:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Instance type '{instance_type}' not available in region '{region}'"
                        )
                    
                    os_pricing = region_data.get(os_type.lower(), {})
                    pricing_details = get_pricing_details(
                        os_pricing, 
                        pricing_type, 
                        ri_term, 
                        ri_payment, 
                        ri_type, 
                        spot_type
                    )
                    
                    if pricing_details and pricing_details.get('price') is not None:
                        # Return just the price as a string (will be converted to plain text)
                        return str(pricing_details['price'])
                    else:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Pricing type '{pricing_type}' not available for this instance"
                        )
            except HTTPException:
                raise
            except Exception as e:
                print(f"Error processing instance {instance.get('instance_type', 'unknown')}: {e}")
                continue
        
        raise HTTPException(
            status_code=404,
            detail=f"Instance type '{instance_type}' not found"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/search")
async def search_instances(
    region: str = 'us-east-1',
    family: str = None,
    min_vcpus: int = None,
    max_vcpus: int = None,
    min_memory: float = None,
    max_memory: float = None,
    min_price: float = None,
    max_price: float = None,
    os_type: str = 'linux',
    limit: int = 50
):
    """
    Search instances with multiple filters
    
    Parameters:
    - region: AWS region code
    - family: Instance family (e.g., t3, m5, c5)
    - min_vcpus: Minimum vCPU count
    - max_vcpus: Maximum vCPU count
    - min_memory: Minimum memory in GB
    - max_memory: Maximum memory in GB
    - min_price: Minimum hourly price
    - max_price: Maximum hourly price
    - os_type: Operating system (linux, windows)
    - limit: Maximum number of results (default 50)
    """
    
    try:
        instances = await fetch_all_instance_data(force_refresh=(pricing_type.lower() == 'spot'))
        
        if not instances:
            raise HTTPException(status_code=503, detail="Unable to fetch pricing data")
        
        results = []
        
        for instance in instances:
            try:
                # Apply filters
                if family and not instance.get('instance_type', '').startswith(family):
                    continue
                
                vcpus = instance.get('vCPU')
                if vcpus:
                    if min_vcpus and vcpus < min_vcpus:
                        continue
                    if max_vcpus and vcpus > max_vcpus:
                        continue
                
                memory = instance.get('memory')
                if memory:
                    if min_memory and memory < min_memory:
                        continue
                    if max_memory and memory > max_memory:
                        continue
                
                # Get pricing
                pricing = instance.get('pricing', {})
                region_data = pricing.get(region, {})
                if not region_data:
                    continue
                
                os_pricing = region_data.get(os_type.lower(), {})
                price = os_pricing.get('ondemand')
                
                if price is None:
                    continue
                
                price = float(price)
                
                if min_price and price < min_price:
                    continue
                if max_price and price > max_price:
                    continue
                
                results.append({
                    "instance_type": instance.get('instance_type'),
                    "vcpus": vcpus,
                    "memory": memory,
                    "storage": instance.get('storage'),
                    "network": instance.get('network_performance'),
                    "family": instance.get('family'),
                    "price": price,
                    "currency": "USD",
                    "unit": "Hrs"
                })
                
                if len(results) >= limit:
                    break
                    
            except Exception as e:
                continue
        
        return {
            "success": True,
            "region": region,
            "os": os_type,
            "filters_applied": {
                "family": family,
                "min_vcpus": min_vcpus,
                "max_vcpus": max_vcpus,
                "min_memory": min_memory,
                "max_memory": max_memory,
                "min_price": min_price,
                "max_price": max_price
            },
            "count": len(results),
            "instances": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/regions")
async def list_regions():
    """List all available AWS regions"""
    
    try:
        instances = await fetch_all_instance_data(force_refresh=(pricing_type.lower() == 'spot'))
        
        if not instances:
            raise HTTPException(status_code=503, detail="Unable to fetch pricing data")
        
        regions = set()
        
        for instance in instances:
            pricing = instance.get('pricing', {})
            regions.update(pricing.keys())
        
        region_list = sorted(list(regions))
        
        return {
            "success": True,
            "count": len(region_list),
            "regions": region_list
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/families")
async def list_families():
    """List all instance families"""
    
    try:
        instances = await fetch_all_instance_data(force_refresh=(pricing_type.lower() == 'spot'))
        
        if not instances:
            raise HTTPException(status_code=503, detail="Unable to fetch pricing data")
        
        families = {}
        
        for instance in instances:
            instance_type = instance.get('instance_type', '')
            family = instance.get('family', instance_type.split('.')[0] if '.' in instance_type else 'unknown')
            
            if family not in families:
                families[family] = {
                    "family": family,
                    "description": instance.get('family_description', ''),
                    "count": 0,
                    "examples": []
                }
            
            families[family]['count'] += 1
            if len(families[family]['examples']) < 3:
                families[family]['examples'].append(instance_type)
        
        return {
            "success": True,
            "count": len(families),
            "families": sorted(families.values(), key=lambda x: x['family'])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/compare")
async def compare_instances(
    instances: str,
    region: str = 'us-east-1',
    os_type: str = 'linux'
):
    """
    Compare multiple instance types
    
    Parameters:
    - instances: Comma-separated list of instance types (e.g., t3.micro,t3.small,t2.micro)
    - region: AWS region code
    - os_type: Operating system (linux, windows)
    """
    
    try:
        instance_list = [i.strip() for i in instances.split(',')]
        
        all_instances = await fetch_all_instance_data()
        
        if not all_instances:
            raise HTTPException(status_code=503, detail="Unable to fetch pricing data")
        
        results = []
        
        for target_type in instance_list:
            for instance in all_instances:
                if instance.get('instance_type') == target_type:
                    pricing = instance.get('pricing', {})
                    region_data = pricing.get(region, {})
                    
                    if region_data:
                        os_pricing = region_data.get(os_type.lower(), {})
                        price = os_pricing.get('ondemand')
                        
                        if price is not None:
                            results.append({
                                "instance_type": target_type,
                                "vcpus": instance.get('vCPU'),
                                "memory": instance.get('memory'),
                                "storage": instance.get('storage'),
                                "network": instance.get('network_performance'),
                                "price": float(price),
                                "price_per_vcpu": round(float(price) / instance.get('vCPU', 1), 4) if instance.get('vCPU') else None,
                                "price_per_gb_memory": round(float(price) / instance.get('memory', 1), 4) if instance.get('memory') else None,
                                "currency": "USD",
                                "unit": "Hrs"
                            })
                    break
        
        return {
            "success": True,
            "region": region,
            "os": os_type,
            "count": len(results),
            "comparison": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/cheapest")
async def get_cheapest_instances(
    region: str = 'us-east-1',
    min_vcpus: int = 1,
    min_memory: float = 1,
    family: str = None,
    os_type: str = 'linux',
    limit: int = 10
):
    """
    Find the cheapest instances matching your requirements
    
    Parameters:
    - region: AWS region code
    - min_vcpus: Minimum vCPU count
    - min_memory: Minimum memory in GB
    - family: Instance family filter (optional)
    - os_type: Operating system (linux, windows)
    - limit: Number of results to return
    """
    
    try:
        instances = await fetch_all_instance_data(force_refresh=(pricing_type.lower() == 'spot'))
        
        if not instances:
            raise HTTPException(status_code=503, detail="Unable to fetch pricing data")
        
        results = []
        
        for instance in instances:
            try:
                # Apply filters
                if family and not instance.get('instance_type', '').startswith(family):
                    continue
                
                vcpus = instance.get('vCPU')
                if not vcpus or vcpus < min_vcpus:
                    continue
                
                memory = instance.get('memory')
                if not memory or memory < min_memory:
                    continue
                
                # Get pricing
                pricing = instance.get('pricing', {})
                region_data = pricing.get(region, {})
                if not region_data:
                    continue
                
                os_pricing = region_data.get(os_type.lower(), {})
                price = os_pricing.get('ondemand')
                
                if price is None:
                    continue
                
                price = float(price)
                
                results.append({
                    "instance_type": instance.get('instance_type'),
                    "vcpus": vcpus,
                    "memory": memory,
                    "storage": instance.get('storage'),
                    "network": instance.get('network_performance'),
                    "price": price,
                    "price_per_vcpu": round(price / vcpus, 4),
                    "price_per_gb_memory": round(price / memory, 4),
                    "monthly_price": round(price * 730, 2),  # 730 hours per month
                    "currency": "USD",
                    "unit": "Hrs"
                })
                    
            except Exception as e:
                continue
        
        # Sort by price
        results.sort(key=lambda x: x['price'])
        results = results[:limit]
        
        return {
            "success": True,
            "region": region,
            "os": os_type,
            "filters": {
                "min_vcpus": min_vcpus,
                "min_memory": min_memory,
                "family": family
            },
            "count": len(results),
            "cheapest_instances": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/instances")
async def list_all_instances(
    region: str = None,
    os_type: str = 'linux',
    include_pricing: bool = True
):
    """
    List all available EC2 instance types
    
    Parameters:
    - region: AWS region code (optional, for pricing)
    - os_type: Operating system (linux, windows)
    - include_pricing: Include pricing information
    """
    
    try:
        instances = await fetch_all_instance_data(force_refresh=(pricing_type.lower() == 'spot'))
        
        if not instances:
            raise HTTPException(status_code=503, detail="Unable to fetch pricing data")
        
        results = []
        
        for instance in instances:
            try:
                instance_info = {
                    "instance_type": instance.get('instance_type'),
                    "family": instance.get('family'),
                    "vcpus": instance.get('vCPUs'),
                    "memory": instance.get('memory'),
                    "storage": instance.get('storage'),
                    "network": instance.get('network_performance'),
                    "processor": instance.get('physical_processor')
                }
                
                if include_pricing and region:
                    pricing = instance.get('pricing', {})
                    region_data = pricing.get(region, {})
                    
                    if region_data:
                        os_pricing = region_data.get(os_type.lower(), {})
                        price = os_pricing.get('ondemand')
                        
                        if price is not None:
                            instance_info['price'] = float(price)
                            instance_info['currency'] = 'USD'
                            instance_info['unit'] = 'Hrs'
                
                results.append(instance_info)
                    
            except Exception as e:
                continue
        
        return {
            "success": True,
            "region": region if region else "all",
            "os": os_type if include_pricing else "n/a",
            "count": len(results),
            "instances": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

