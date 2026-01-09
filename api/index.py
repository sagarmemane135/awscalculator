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

@app.get("/")
def root():
    return {
        "message": "AWS EC2 Pricing API - No Authentication Required!",
        "endpoints": {
            "get_price": {
                "path": "/get-price",
                "description": "Get price for a specific instance type",
                "example": "/get-price?instance_type=t3.micro&region=ap-south-1"
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
                "description": "Get only the price value (number only, no JSON)",
                "example": "/get-price-value?instance_type=t3.micro&region=us-east-1"
            }
        },
        "data_source": "instances.vantage.sh (powered by ec2instances.info)"
    }

async def fetch_all_instance_data():
    """Fetch and cache all EC2 instance data"""
    
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

@app.get("/get-price")
async def get_aws_price(
    instance_type: str,
    region: str = 'ap-south-1',
    os_type: str = 'linux',
    pricing_type: str = 'ondemand'
):
    """
    Get EC2 instance pricing
    
    Parameters:
    - instance_type: EC2 instance type (e.g., t3.micro)
    - region: AWS region code (e.g., ap-south-1, us-east-1)
    - os_type: Operating system (linux, windows, rhel, sles, mswinSQLWeb, mswinSQLStd)
    - pricing_type: ondemand, reserved, spot
    """
    
    try:
        instances = await fetch_all_instance_data()
        
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
                    region_price = os_pricing.get(pricing_type.lower())
                    
                    if region_price is not None:
                        return {
                            "success": True,
                            "instance": instance_type,
                            "region": region,
                            "os": os_type,
                            "pricing_type": pricing_type,
                            "price": float(region_price),
                            "currency": "USD",
                            "unit": "Hrs",
                            "specs": {
                                "vcpus": instance.get('vCPU'),
                                "memory": instance.get('memory'),
                                "storage": instance.get('storage'),
                                "network": instance.get('network_performance'),
                                "family": instance.get('family'),
                                "processor": instance.get('physical_processor')
                            }
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
    pricing_type: str = 'ondemand'
):
    """
    Get only the price value as a number (no JSON, just the price)
    
    Returns: Just the price number (e.g., "0.0104")
    
    Parameters:
    - instance_type: EC2 instance type (e.g., t3.micro)
    - region: AWS region code (e.g., ap-south-1, us-east-1)
    - os_type: Operating system (linux, windows, rhel, sles)
    - pricing_type: ondemand, reserved, spot
    """
    
    try:
        instances = await fetch_all_instance_data()
        
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
                    region_price = os_pricing.get(pricing_type.lower())
                    
                    if region_price is not None:
                        # Return just the price as a string (will be converted to plain text)
                        return str(float(region_price))
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
        instances = await fetch_all_instance_data()
        
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
        instances = await fetch_all_instance_data()
        
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
        instances = await fetch_all_instance_data()
        
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
        instances = await fetch_all_instance_data()
        
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
        instances = await fetch_all_instance_data()
        
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

