# Available Filters - Quick Reference

## 🎯 All Available Filters

Your AWS EC2 Pricing API now supports **15+ different filters** across multiple endpoints!

---

## 📊 Filter Categories

### 1. **Instance Selection Filters**

| Filter | Type | Endpoints | Description | Example |
|--------|------|-----------|-------------|---------|
| `instance_type` | string | `/get-price`, `/compare` | Specific instance type | `t3.micro` |
| `instances` | string | `/compare` | Multiple instances (comma-separated) | `t3.micro,t3.small` |
| `family` | string | `/search`, `/cheapest` | Instance family prefix | `t3`, `m5`, `c5` |

### 2. **Compute Resource Filters**

| Filter | Type | Endpoints | Description | Example |
|--------|------|-----------|-------------|---------|
| `min_vcpus` | integer | `/search`, `/cheapest` | Minimum vCPU count | `2` |
| `max_vcpus` | integer | `/search` | Maximum vCPU count | `8` |
| `min_memory` | float | `/search`, `/cheapest` | Minimum memory (GB) | `4.0` |
| `max_memory` | float | `/search` | Maximum memory (GB) | `16.0` |

### 3. **Pricing Filters**

| Filter | Type | Endpoints | Description | Example |
|--------|------|-----------|-------------|---------|
| `min_price` | float | `/search` | Minimum hourly price (USD) | `0.01` |
| `max_price` | float | `/search` | Maximum hourly price (USD) | `0.10` |
| `pricing_type` | string | `/get-price` | Pricing model | `ondemand`, `reserved`, `spot` |

### 4. **Location & OS Filters**

| Filter | Type | Endpoints | Description | Example |
|--------|------|-----------|-------------|---------|
| `region` | string | All | AWS region code | `us-east-1`, `ap-south-1` |
| `os_type` | string | Most | Operating system | `linux`, `windows`, `rhel` |

### 5. **Result Control Filters**

| Filter | Type | Endpoints | Description | Example |
|--------|------|-----------|-------------|---------|
| `limit` | integer | `/search`, `/cheapest` | Maximum results returned | `10`, `50` |
| `include_pricing` | boolean | `/instances` | Include price data | `true`, `false` |

---

## 🔍 Filter Combinations by Endpoint

### `/get-price` - 4 Filters
- `instance_type` (required)
- `region`
- `os_type`
- `pricing_type`

### `/search` - 10 Filters
- `region`
- `family`
- `min_vcpus`
- `max_vcpus`
- `min_memory`
- `max_memory`
- `min_price`
- `max_price`
- `os_type`
- `limit`

### `/compare` - 3 Filters
- `instances` (required)
- `region`
- `os_type`

### `/cheapest` - 6 Filters
- `region`
- `min_vcpus`
- `min_memory`
- `family`
- `os_type`
- `limit`

### `/instances` - 3 Filters
- `region`
- `os_type`
- `include_pricing`

### `/regions` - 0 Filters
Returns all 103 regions

### `/families` - 0 Filters
Returns all 9 instance families

---

## 💡 Common Filter Patterns

### Pattern 1: Find Budget Instances
```bash
# Instances under $0.05/hour with at least 2 vCPUs
curl "https://awscalculator.vercel.app/search?max_price=0.05&min_vcpus=2&region=us-east-1"
```

### Pattern 2: Memory-Heavy Workloads
```bash
# Instances with 16-32 GB memory
curl "https://awscalculator.vercel.app/search?min_memory=16&max_memory=32&region=us-east-1"
```

### Pattern 3: Family Comparison
```bash
# Compare all t3 instances
curl "https://awscalculator.vercel.app/search?family=t3&region=us-east-1"
```

### Pattern 4: Cost Optimization
```bash
# Find 10 cheapest instances with minimum specs
curl "https://awscalculator.vercel.app/cheapest?min_vcpus=4&min_memory=8&limit=10"
```

### Pattern 5: Specific Region Analysis
```bash
# All m5 family in Mumbai
curl "https://awscalculator.vercel.app/search?family=m5&region=ap-south-1"
```

### Pattern 6: Price Range Search
```bash
# Instances between $0.10 and $0.50 per hour
curl "https://awscalculator.vercel.app/search?min_price=0.10&max_price=0.50&region=us-east-1"
```

---

## 📈 Filter Limits & Defaults

| Setting | Default | Maximum | Notes |
|---------|---------|---------|-------|
| `limit` | 50 | No hard limit | Performance may degrade with very large results |
| `region` | `ap-south-1` or `us-east-1` | - | Depends on endpoint |
| `os_type` | `linux` | - | Most common use case |
| `pricing_type` | `ondemand` | - | Most common pricing model |

---

## 🎓 Advanced Filtering Tips

### Tip 1: Combine Multiple Filters
```bash
# Find t3 instances with 2-4 vCPUs, 4-8GB memory, under $0.10/hour
curl "https://awscalculator.vercel.app/search?family=t3&min_vcpus=2&max_vcpus=4&min_memory=4&max_memory=8&max_price=0.10"
```

### Tip 2: Use Limit for Quick Results
```bash
# Get just top 5 results
curl "https://awscalculator.vercel.app/search?family=t3&limit=5"
```

### Tip 3: Compare Before Committing
```bash
# Compare multiple options side by side
curl "https://awscalculator.vercel.app/compare?instances=t3.medium,t3a.medium,t2.medium&region=us-east-1"
```

### Tip 4: Find Bargains
```bash
# Cheapest instances in a specific family
curl "https://awscalculator.vercel.app/cheapest?family=m5&region=us-east-1&limit=3"
```

---

## 🌍 Supported Values

### Regions (103 total)
- **US**: `us-east-1`, `us-east-2`, `us-west-1`, `us-west-2`
- **Europe**: `eu-west-1`, `eu-west-2`, `eu-west-3`, `eu-central-1`, `eu-north-1`
- **Asia Pacific**: `ap-south-1`, `ap-southeast-1`, `ap-southeast-2`, `ap-northeast-1`, `ap-northeast-2`
- **Other**: `ca-central-1`, `sa-east-1`, `me-south-1`, `af-south-1`
- [See full list via `/regions` endpoint]

### Instance Families (9 categories)
- General purpose
- Compute optimized
- Memory optimized
- Storage optimized
- GPU instance
- FPGA Instances
- Machine Learning ASIC Instances
- Media Accelerator Instances
- Micro instances

### Operating Systems
- `linux` (most common)
- `windows`
- `rhel`
- `sles`
- `mswinSQLWeb`
- `mswinSQLStd`

### Pricing Types
- `ondemand` (pay as you go)
- `reserved` (commitment discount)
- `spot` (interruptible, cheapest)

---

## ⚠️ Important Notes

1. **Case Sensitivity**: Most filters are case-insensitive, but instance types are case-sensitive
2. **Partial Matches**: Family filter uses prefix matching (e.g., `t3` matches `t3.micro`, `t3.small`)
3. **Null Values**: Some spec values may be null in the data
4. **Price Currency**: All prices are in USD per hour
5. **Caching**: Data is cached for 1 hour for performance

---

## 🚀 Quick Start Examples

```bash
# 1. Simple price lookup
curl "https://awscalculator.vercel.app/get-price?instance_type=t3.micro&region=us-east-1"

# 2. Find cheap options
curl "https://awscalculator.vercel.app/cheapest?min_vcpus=2&min_memory=4&limit=5"

# 3. Compare similar instances
curl "https://awscalculator.vercel.app/compare?instances=t3.small,t3a.small,t2.small"

# 4. Search with filters
curl "https://awscalculator.vercel.app/search?family=m5&min_memory=16&region=us-west-2"

# 5. List all regions
curl "https://awscalculator.vercel.app/regions"
```

---

**Total Available Filters: 15+**
**Total Endpoints: 7**
**Total Regions: 103**
**Total Instance Families: 9**

