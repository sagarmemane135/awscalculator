# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-09

### Added
- Initial release of AWS EC2 Pricing API
- 7 API endpoints for EC2 pricing queries
- 15+ filters for advanced instance search
- Support for 103 AWS regions
- Real-time pricing data from instances.vantage.sh
- Excel integration support
- Comprehensive API documentation
- FastAPI-based REST API
- Vercel deployment configuration

### Features
- `GET /get-price` - Get price for specific instance
- `GET /search` - Advanced search with multiple filters
- `GET /compare` - Compare multiple instances side-by-side
- `GET /cheapest` - Find cheapest instances matching criteria
- `GET /regions` - List all available AWS regions
- `GET /families` - List all instance families
- `GET /instances` - List all instance types

### Fixed
- Corrected vCPU field name from `vCPUs` to `vCPU`
- Fixed storage field handling for instances with/without local storage
- Improved error handling and response formatting

### Documentation
- Complete API documentation (API_DOCUMENTATION.md)
- Filters reference guide (FILTERS_SUMMARY.md)
- Usage examples for Python, JavaScript, cURL, and Excel
- Deployment instructions
- Contributing guidelines

## [1.1.0] - 2024-01-09

### Added
- **Reserved Instance Pricing Support** - Full support for all Reserved Instance options
  - Term options: 1-year and 3-year
  - Payment options: All Upfront, Partial Upfront, No Upfront
  - RI types: Standard, Convertible, Savings Plans
  - Parameters: `ri_term`, `ri_payment`, `ri_type`
- **Spot Instance Pricing Support** - Support for Spot pricing with min/max/avg options
  - Spot type selection: `min`, `max`, `avg`
  - Includes savings percentage and interruption rate
  - Parameter: `spot_type`
- **Enhanced `/get-price-value` endpoint** - Now supports all pricing types (On-Demand, Reserved, Spot)
- **Comprehensive pricing details** - Responses include pricing info and all available options
- **Helper functions** for extracting Reserved Instance and Spot pricing

### Enhanced
- `/get-price` endpoint now supports full Reserved Instance and Spot pricing
- `/get-price-value` endpoint now supports all pricing types
- Improved error messages for pricing type availability
- Better handling of pricing data structures

### Examples
```bash
# Reserved Instance - 1 year, Standard, No Upfront
/get-price?instance_type=t3.micro&pricing_type=reserved&ri_term=1yr&ri_payment=noUpfront&ri_type=Standard

# Reserved Instance - 3 year, Savings Plan, All Upfront  
/get-price?instance_type=t3.micro&pricing_type=reserved&ri_term=3yr&ri_payment=allUpfront&ri_type=Savings

# Spot Instance - Average price
/get-price?instance_type=t3.micro&pricing_type=spot&spot_type=avg
```

## [Unreleased]

### Planned
- Price history tracking
- Rate limiting and usage analytics
- OpenAPI/Swagger documentation endpoint

