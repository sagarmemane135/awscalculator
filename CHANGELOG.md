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

## [Unreleased]

### Planned
- Support for Reserved Instance pricing
- Support for Spot Instance pricing
- Price history tracking
- Rate limiting and usage analytics
- OpenAPI/Swagger documentation endpoint

