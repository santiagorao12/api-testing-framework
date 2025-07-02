# config.py - Configuration Management
class Config:
    """API Testing Framework Configuration"""
    
    # Base URLs
    JSONPLACEHOLDER_BASE_URL = "https://jsonplaceholder.typicode.com"
    REQRES_BASE_URL = "https://reqres.in/api"
    
    # Test Data
    TEST_USER_DATA = {
        "name": "John Doe",
        "job": "QA Automation Engineer"
    }
    
    TEST_POST_DATA = {
        "title": "Test Post Title",
        "body": "This is a test post body for API testing",
        "userId": 1
    }
    
    # Test Credentials (ReqRes valid test credentials)
    VALID_LOGIN = {
        "email": "eve.holt@reqres.in",
        "password": "cityslicka"
    }
    
    VALID_REGISTER = {
        "email": "eve.holt@reqres.in",
        "password": "pistol"
    }
    
    # Test Settings
    RESPONSE_TIMEOUT = 5  # seconds
    MAX_RESPONSE_TIME = 3000  # milliseconds (increased for external APIs)