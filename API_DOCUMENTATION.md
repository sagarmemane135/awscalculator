# AWS EC2 Pricing API - Complete Documentation

## Base URL
```
https://awscalculator.vercel.app
```

---

## 📋 Available Endpoints

### 1. **GET /** - API Information
Returns information about all available endpoints.

**Example:**
```bash
curl "https://awscalculator.vercel.app/"
```

---

### 2. **GET /get-price** - Get Single Instance Price

Get pricing for a specific EC2 instance type.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `instance_type` | string | Yes | - | EC2 instance type (e.g., t3.micro) |
| `region` | string | No | `ap-south-1` | AWS region code |
| `os_type` | string | No | `linux` | Operating system (linux, windows, rhel, sles) |
| `pricing_type` | string | No | `ondemand` | Pricing type (ondemand, reserved, spot) |

**Example Requests:**
```bash
# Basic usage
curl "https://awscalculator.vercel.app/get-price?instance_type=t3.micro&region=us-east-1"

# With Windows pricing
curl "https://awscalculator.vercel.app/get-price?instance_type=t3.micro&region=us-east-1&os_type=windows"

# Different region
curl "https://awscalculator.vercel.app/get-price?instance_type=m5.large&region=eu-west-1"
```

**Response:**
```json
{
  "success": true,
  "instance": "t3.micro",
  "region": "us-east-1",
  "os": "linux",
  "pricing_type": "ondemand",
  "price": 0.0104,
  "currency": "USD",
  "unit": "Hrs",
  "specs": {
    "vcpus": null,
    "memory": 1,
    "storage": null,
    "network": "Up to 5 Gigabit",
    "family": "General purpose",
    "processor": "..."
  }
}
```

---

### 2. **GET /get-price-value** - Get Only Price Value

Get just the price as a plain number (no JSON, no metadata).

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `instance_type` | string | Yes | - | EC2 instance type (e.g., t3.micro) |
| `region` | string | No | `ap-south-1` | AWS region code |
| `os_type` | string | No | `linux` | Operating system |
| `pricing_type` | string | No | `ondemand` | Pricing type (ondemand, reserved, spot) |

**Example Requests:**
```bash
# Get just the price number
curl "https://awscalculator.vercel.app/get-price-value?instance_type=t3.micro&region=us-east-1"

# Jakarta region
curl "https://awscalculator.vercel.app/get-price-value?instance_type=t3.micro&region=ap-southeast-3"
```

**Response:**
```
0.0104
```
*(Just the number - perfect for Excel, simple scripts, or when you only need the price!)*

**Use Cases:**
- Excel formulas (no JSON parsing needed)
- Simple bash scripts
- Quick price lookups
- When you only need the numeric value

---

### 3. **GET /search** - Search Instances with Filters

Search for instances matching specific criteria.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `region` | string | No | `us-east-1` | AWS region code |
| `family` | string | No | - | Instance family (e.g., t3, m5, c5) |
| `min_vcpus` | integer | No | - | Minimum vCPU count |
| `max_vcpus` | integer | No | - | Maximum vCPU count |
| `min_memory` | float | No | - | Minimum memory in GB |
| `max_memory` | float | No | - | Maximum memory in GB |
| `min_price` | float | No | - | Minimum hourly price |
| `max_price` | float | No | - | Maximum hourly price |
| `os_type` | string | No | `linux` | Operating system |
| `limit` | integer | No | `50` | Maximum number of results |

**Example Requests:**
```bash
# Find instances with 2-4 vCPUs and 4-8 GB memory
curl "https://awscalculator.vercel.app/search?min_vcpus=2&max_vcpus=4&min_memory=4&max_memory=8&region=us-east-1"

# Find all t3 family instances
curl "https://awscalculator.vercel.app/search?family=t3&region=us-east-1"

# Find cheap instances under $0.05/hour
curl "https://awscalculator.vercel.app/search?max_price=0.05&region=us-east-1&limit=10"

# Find instances with specific memory
curl "https://awscalculator.vercel.app/search?min_memory=8&max_memory=16&region=ap-south-1"
```

**Response:**
```json
{
  "success": true,
  "region": "us-east-1",
  "os": "linux",
  "filters_applied": {
    "family": "t3",
    "min_vcpus": null,
    "max_vcpus": null,
    "min_memory": null,
    "max_memory": null,
    "min_price": null,
    "max_price": null
  },
  "count": 5,
  "instances": [
    {
      "instance_type": "t3.micro",
      "vcpus": null,
      "memory": 1,
      "storage": null,
      "network": "Up to 5 Gigabit",
      "family": "General purpose",
      "price": 0.0104,
      "currency": "USD",
      "unit": "Hrs"
    }
  ]
}
```

---

### 4. **GET /compare** - Compare Multiple Instances

Compare pricing and specs of multiple instance types side by side.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `instances` | string | Yes | - | Comma-separated list of instance types |
| `region` | string | No | `us-east-1` | AWS region code |
| `os_type` | string | No | `linux` | Operating system |

**Example Requests:**
```bash
# Compare t3 instances
curl "https://awscalculator.vercel.app/compare?instances=t3.micro,t3.small,t3.medium&region=us-east-1"

# Compare different families
curl "https://awscalculator.vercel.app/compare?instances=t3.micro,t2.micro,t4g.micro&region=us-east-1"
```

**Response:**
```json
{
  "success": true,
  "region": "us-east-1",
  "os": "linux",
  "count": 3,
  "comparison": [
    {
      "instance_type": "t3.micro",
      "vcpus": null,
      "memory": 1,
      "storage": null,
      "network": "Up to 5 Gigabit",
      "price": 0.0104,
      "price_per_vcpu": null,
      "price_per_gb_memory": 0.0104,
      "currency": "USD",
      "unit": "Hrs"
    }
  ]
}
```

---

### 5. **GET /cheapest** - Find Cheapest Instances

Find the cheapest instances that meet your minimum requirements.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `region` | string | No | `us-east-1` | AWS region code |
| `min_vcpus` | integer | No | `1` | Minimum vCPU count |
| `min_memory` | float | No | `1` | Minimum memory in GB |
| `family` | string | No | - | Instance family filter |
| `os_type` | string | No | `linux` | Operating system |
| `limit` | integer | No | `10` | Number of results |

**Example Requests:**
```bash
# Find 5 cheapest instances with at least 2 vCPUs and 4GB memory
curl "https://awscalculator.vercel.app/cheapest?min_vcpus=2&min_memory=4&region=us-east-1&limit=5"

# Find cheapest t3 instances
curl "https://awscalculator.vercel.app/cheapest?family=t3&region=us-east-1"
```

**Response:**
```json
{
  "success": true,
  "region": "us-east-1",
  "os": "linux",
  "filters": {
    "min_vcpus": 2,
    "min_memory": 4.0,
    "family": null
  },
  "count": 5,
  "cheapest_instances": [
    {
      "instance_type": "t3.medium",
      "vcpus": null,
      "memory": 4,
      "storage": null,
      "network": "Up to 5 Gigabit",
      "price": 0.0416,
      "price_per_vcpu": 0.0208,
      "price_per_gb_memory": 0.0104,
      "monthly_price": 30.37,
      "currency": "USD",
      "unit": "Hrs"
    }
  ]
}
```

---

### 6. **GET /regions** - List All Regions

Get a list of all available AWS regions.

**Example Request:**
```bash
curl "https://awscalculator.vercel.app/regions"
```

**Response:**
```json
{
  "success": true,
  "count": 103,
  "regions": [
    "af-south-1",
    "ap-east-1",
    "ap-northeast-1",
    "ap-south-1",
    "us-east-1",
    "us-west-2",
    "..."
  ]
}
```

---

### 7. **GET /families** - List Instance Families

Get all available instance families with examples.

**Example Request:**
```bash
curl "https://awscalculator.vercel.app/families"
```

**Response:**
```json
{
  "success": true,
  "count": 9,
  "families": [
    {
      "family": "General purpose",
      "description": "",
      "count": 306,
      "examples": ["a1.2xlarge", "a1.4xlarge", "a1.large"]
    },
    {
      "family": "Compute optimized",
      "description": "",
      "count": 266,
      "examples": ["c1.medium", "c1.xlarge", "c3.2xlarge"]
    }
  ]
}
```

---

### 8. **GET /instances** - List All Instances

Get a list of all available EC2 instance types.

**Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `region` | string | No | - | AWS region for pricing |
| `os_type` | string | No | `linux` | Operating system |
| `include_pricing` | boolean | No | `true` | Include pricing data |

**Example Requests:**
```bash
# List all instances with US East pricing
curl "https://awscalculator.vercel.app/instances?region=us-east-1"

# List all instances without pricing
curl "https://awscalculator.vercel.app/instances?include_pricing=false"
```

---

## 🔧 Common Use Cases

### Excel Integration

**Recommended: Get just the price (no JSON parsing needed)**
```excel
=WEBSERVICE("https://awscalculator.vercel.app/get-price-value?instance_type=" & A2 & "&region=us-east-1")
```

**Alternative: Get full JSON response**
```excel
=WEBSERVICE("https://awscalculator.vercel.app/get-price?instance_type=" & A2 & "&region=us-east-1")
```
*Then parse the JSON response to extract the price field.*

### Python
```python
import requests

response = requests.get(
    "https://awscalculator.vercel.app/get-price",
    params={
        "instance_type": "t3.micro",
        "region": "us-east-1"
    }
)
print(response.json()["price"])
```

### JavaScript
```javascript
fetch('https://awscalculator.vercel.app/get-price?instance_type=t3.micro&region=us-east-1')
  .then(response => response.json())
  .then(data => console.log(data.price));
```

---

## 📊 Available Filters Summary

| Filter Type | Endpoints | Description |
|------------|-----------|-------------|
| **Instance Type** | `/get-price`, `/compare` | Specific instance (e.g., t3.micro) |
| **Region** | All | AWS region code (103 regions available) |
| **Instance Family** | `/search`, `/cheapest` | Instance family (t3, m5, c5, etc.) |
| **vCPU Range** | `/search` | Min/max vCPU count |
| **Memory Range** | `/search`, `/cheapest` | Min/max memory in GB |
| **Price Range** | `/search` | Min/max hourly price |
| **Operating System** | Most endpoints | linux, windows, rhel, sles |
| **Pricing Type** | `/get-price` | ondemand, reserved, spot |
| **Result Limit** | `/search`, `/cheapest` | Limit number of results |

---

## 🌍 Popular Regions

| Region Code | Location |
|-------------|----------|
| `us-east-1` | US East (N. Virginia) |
| `us-west-2` | US West (Oregon) |
| `eu-west-1` | Europe (Ireland) |
| `ap-south-1` | Asia Pacific (Mumbai) |
| `ap-southeast-1` | Asia Pacific (Singapore) |
| `ap-northeast-1` | Asia Pacific (Tokyo) |

---

## ⚡ Performance

- **Caching**: 1-hour cache for pricing data
- **Response Time**: ~200-500ms average
- **Rate Limits**: None (public API)
- **Availability**: 99.9% (Vercel edge network)

---

## 🔒 Security

- ✅ No authentication required
- ✅ No AWS credentials needed
- ✅ Read-only access to pricing data
- ✅ CORS enabled for browser requests

---

## 📝 Error Responses

```json
{
  "error": "Instance type 't3.micro' not available in region 'xyz-region-1'",
  "instance_info": {
    "type": "t3.micro",
    "vcpus": null,
    "memory": 1,
    "available_regions": ["us-east-1", "us-west-2", "..."]
  }
}
```

---

## 🆘 Support

For issues or questions:
- GitHub: [Your Repository]
- Data Source: [instances.vantage.sh](https://instances.vantage.sh)

