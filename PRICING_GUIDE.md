# AWS EC2 Pricing Guide

Complete guide to using all pricing options in the AWS EC2 Pricing API.

## 📊 Pricing Types Overview

The API supports three main pricing models:

1. **On-Demand** - Pay-as-you-go (default)
2. **Reserved Instances** - Commit to 1 or 3 years for discounts
3. **Spot Instances** - Use spare capacity at lower prices

---

## 💰 On-Demand Pricing

**Simplest pricing model** - Pay only for what you use, no commitment.

### Usage
```bash
# Basic on-demand pricing
curl "https://awscalculator.vercel.app/get-price-value?instance_type=t3.micro&region=us-east-1"

# Or explicitly specify
curl "https://awscalculator.vercel.app/get-price-value?instance_type=t3.micro&region=us-east-1&pricing_type=ondemand"
```

### Response
```
0.0104
```

### When to Use
- ✅ Variable workloads
- ✅ Short-term projects
- ✅ Testing and development
- ✅ No upfront commitment needed

---

## 💳 Reserved Instance Pricing

**Save up to 72%** compared to On-Demand by committing to 1 or 3 years.

### Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `ri_term` | `1yr`, `3yr` | Commitment term length |
| `ri_payment` | `allUpfront`, `partialUpfront`, `noUpfront` | Payment option |
| `ri_type` | `Standard`, `Convertible`, `Savings` | RI type |

### Reserved Instance Types

#### Standard Reserved Instances
- **Best for**: Predictable workloads
- **Flexibility**: Can't change instance type
- **Discount**: Up to 72% off On-Demand

#### Convertible Reserved Instances
- **Best for**: Workloads that might change
- **Flexibility**: Can change instance type/family
- **Discount**: Up to 54% off On-Demand

#### Savings Plans
- **Best for**: Consistent usage across instance families
- **Flexibility**: Most flexible - applies to any instance
- **Discount**: Up to 66% off On-Demand

### Payment Options

#### All Upfront
- Pay entire amount at purchase
- **Highest discount**
- Best for: Long-term predictable costs

#### Partial Upfront
- Pay portion upfront, rest monthly
- **Moderate discount**
- Best for: Balanced approach

#### No Upfront
- Pay nothing upfront, monthly payments
- **Lowest discount**
- Best for: Cash flow management

### Examples

```bash
# 1-year Standard RI, No Upfront (most common)
curl "https://awscalculator.vercel.app/get-price-value?instance_type=t3.micro&region=us-east-1&pricing_type=reserved&ri_term=1yr&ri_payment=noUpfront&ri_type=Standard"

# 3-year Savings Plan, All Upfront (best discount)
curl "https://awscalculator.vercel.app/get-price-value?instance_type=t3.micro&region=us-east-1&pricing_type=reserved&ri_term=3yr&ri_payment=allUpfront&ri_type=Savings"

# 1-year Convertible, Partial Upfront
curl "https://awscalculator.vercel.app/get-price-value?instance_type=t3.micro&region=us-east-1&pricing_type=reserved&ri_term=1yr&ri_payment=partialUpfront&ri_type=Convertible"
```

### Full Response Example
```json
{
  "success": true,
  "instance": "t3.micro",
  "region": "us-east-1",
  "pricing_type": "reserved",
  "price": 0.0065,
  "pricing_info": {
    "type": "Reserved Instance",
    "term": "1yr",
    "payment": "noUpfront",
    "ri_type": "Standard",
    "description": "Standard RI - 1yr - noUpfront"
  },
  "all_reserved_options": {
    "yrTerm1Standard.allUpfront": "0.00605",
    "yrTerm1Standard.noUpfront": "0.0065",
    "yrTerm1Standard.partialUpfront": "0.006182",
    "yrTerm3Standard.allUpfront": "0.003919",
    "...": "18 total options"
  }
}
```

### Cost Comparison Example

For **t3.micro in us-east-1**:
- **On-Demand**: $0.0104/hour = **$7.59/month**
- **1yr Standard RI (No Upfront)**: $0.0065/hour = **$4.75/month** (37% savings)
- **3yr Standard RI (All Upfront)**: $0.003919/hour = **$2.86/month** (62% savings)

---

## ⚡ Spot Instance Pricing

**Save up to 90%** by using AWS's spare capacity. Prices fluctuate based on supply and demand.

### Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `spot_type` | `min`, `max`, `avg` | Which spot price to retrieve |

### Spot Price Types

#### Minimum (`min`)
- Lowest historical spot price
- **Best case scenario**
- Use for: Cost planning (best case)

#### Maximum (`max`)
- Highest historical spot price
- **Worst case scenario**
- Use for: Cost planning (worst case)

#### Average (`avg`)
- Average historical spot price
- **Most realistic estimate**
- Use for: Budget planning (recommended)

### Examples

```bash
# Average spot price (recommended)
curl "https://awscalculator.vercel.app/get-price-value?instance_type=t3.micro&region=us-east-1&pricing_type=spot&spot_type=avg"

# Minimum spot price
curl "https://awscalculator.vercel.app/get-price-value?instance_type=t3.micro&region=us-east-1&pricing_type=spot&spot_type=min"

# Maximum spot price
curl "https://awscalculator.vercel.app/get-price-value?instance_type=t3.micro&region=us-east-1&pricing_type=spot&spot_type=max"
```

### Full Response Example
```json
{
  "success": true,
  "instance": "t3.micro",
  "region": "us-east-1",
  "pricing_type": "spot",
  "price": 0.0039,
  "pricing_info": {
    "type": "Spot Instance",
    "spot_type": "avg",
    "description": "Spot pricing (avg)"
  },
  "spot_details": {
    "min": 0.0032,
    "max": 0.0044,
    "avg": 0.0039,
    "savings_vs_ondemand": 62.5,
    "interruption_rate": 5.0
  }
}
```

### Important Notes

⚠️ **Spot Instances can be interrupted** - AWS can reclaim capacity with 2-minute notice
✅ **Best for**: Fault-tolerant, flexible workloads
❌ **Not for**: Critical, always-on applications

### When to Use Spot Instances
- ✅ Batch processing
- ✅ Data analysis
- ✅ CI/CD workloads
- ✅ Development/testing
- ✅ Fault-tolerant applications

---

## 📈 Pricing Comparison

### Example: t3.micro in us-east-1

| Pricing Type | Hourly Price | Monthly Cost | Savings vs On-Demand |
|--------------|--------------|--------------|---------------------|
| **On-Demand** | $0.0104 | $7.59 | Baseline |
| **1yr RI (No Upfront)** | $0.0065 | $4.75 | **37%** |
| **3yr RI (All Upfront)** | $0.003919 | $2.86 | **62%** |
| **Spot (Average)** | $0.0039 | $2.85 | **62%** |

---

## 🎯 Choosing the Right Pricing Model

### Use On-Demand If:
- Workload is unpredictable
- Short-term project (< 1 year)
- Need maximum flexibility
- Testing/development

### Use Reserved Instances If:
- Predictable, steady workload
- Running 24/7 for 1+ years
- Want guaranteed capacity
- Can commit to term

### Use Spot Instances If:
- Workload is fault-tolerant
- Can handle interruptions
- Need maximum cost savings
- Flexible timing requirements

---

## 💡 Pro Tips

1. **Compare all options** - Use the API to compare On-Demand, RI, and Spot
2. **Regional differences** - Prices vary by region, check multiple regions
3. **RI optimization** - 3-year All Upfront gives best discount
4. **Spot monitoring** - Spot prices change, use average for planning
5. **Mix strategies** - Use RI for base load, Spot for variable load

---

## 🔗 Quick Links

- [Complete API Documentation](API_DOCUMENTATION.md)
- [Filters Reference](FILTERS_SUMMARY.md)
- [Live API](https://awscalculator.vercel.app)

