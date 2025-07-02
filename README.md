# API Testing Framework

## Project Overview
Comprehensive Python-based API testing framework with modular architecture for systematic REST API validation across multiple domains.

## 🎯 What This Project Does
Tests the "behind-the-scenes" connections that make websites work. APIs are how different parts of software talk to each other. This framework automatically tests these connections to make sure data is sent and received correctly.

## 🔧 Technical Architecture
- **Language:** Python 3.8+
- **Testing Framework:** pytest
- **HTTP Client:** requests library
- **Configuration:** Centralized config management
- **Reporting:** HTML + JSON reports

## 📊 Performance Metrics
- **Test Cases:** 33 across 5 modules
- **Success Rate:** 100%
- **Average Response Time:** 628ms
- **Concurrent Load Testing:** 20 users
- **Coverage:** All CRUD operations + security scenarios

## 🧪 Testing Modules

### Module 1: CRUD Operations (8 tests)
- GET requests with various parameters
- POST data creation and validation
- PUT updates and data integrity
- DELETE operations and cleanup

### Module 2: Security & Authentication (8 tests)
- HTTPS validation
- CORS policy testing
- SQL injection prevention
- XSS protection validation

### Module 3: Data Relationships (7 tests)
- Nested resource testing
- Data filtering and pagination
- Relationship integrity validation

### Module 4: Error Handling (6 tests)
- 404 not found scenarios
- Malformed request handling
- Boundary condition testing

### Module 5: Performance Testing (6 tests)
- Response time benchmarking
- Concurrent load simulation
- Stress testing scenarios

## 📁 Framework Structure
api-testing-framework/
├── README.md
├── config/
│   └── config.py          # Centralized configuration
├── tests/
│   ├── test_group_1_crud.py
│   ├── test_group_2_auth.py
│   ├── test_group_3_relationships.py
│   ├── test_group_4_errors.py
│   └── test_group_5_performance.py
├── utils/
│   ├── api_client.py      # HTTP client wrapper
│   └── test_helpers.py    # Utility functions
├── reports/               # Test execution reports
└── requirements.txt

## 🚀 Quick Start
```bash
# Clone repository
git clone https://github.com/santiagorao12/api-testing-framework.git

# Install dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest

# Run specific module
pytest tests/test_group_1_crud.py -v

# Generate detailed report
pytest --html=reports/report.html
