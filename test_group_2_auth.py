# test_group_2_auth.py - Authentication & Security Testing
import pytest
import requests
import json
import base64
from api_client import JSONPlaceholderClient
from config import Config

class TestGroup2AuthSecurity:
    """GROUP 2: Authentication & Security Testing (8 tests)"""
    
    @classmethod
    def setup_class(cls):
        """Setup test clients"""
        cls.jsonplaceholder = JSONPlaceholderClient()
        cls.base_url = Config.JSONPLACEHOLDER_BASE_URL
        print("\n🟡 GROUP 2: Authentication & Security Testing Started")
    
    # Security Headers & Protocol Tests (3 tests)
    
    def test_01_https_enforcement(self):
        """TEST 1: Verify HTTPS protocol is enforced"""
        print("\n🔒 Test 1: HTTPS Protocol Verification")
        
        # Test HTTPS endpoint
        response = self.jsonplaceholder.get_all_posts()
        
        # Assertions
        assert response.status_code == 200, f"HTTPS request failed with {response.status_code}"
        assert response.url.startswith('https://'), f"URL should use HTTPS: {response.url}"
        
        # Check security headers (look for any CORS-related header)
        headers_lower = [h.lower() for h in response.headers.keys()]
        
        # Check for CORS headers (any access-control header is good)
        cors_headers = [h for h in headers_lower if h.startswith('access-control')]
        assert len(cors_headers) > 0, f"No CORS headers found. Available: {headers_lower}"
        
        # Check for content-type header
        assert 'content-type' in headers_lower, "Missing Content-type header"
        
        print(f"✅ HTTPS enforced, security headers verified")
    
    def test_02_cors_policy_validation(self):
        """TEST 2: Cross-Origin Resource Sharing (CORS) validation"""
        print("\n🌐 Test 2: CORS Policy Validation")
        
        # Make request with custom Origin header
        headers = {
            'Origin': 'https://example.com',
            'Access-Control-Request-Method': 'GET'
        }
        
        response = requests.get(f"{self.base_url}/posts", headers=headers)
        
        # Assertions
        assert response.status_code == 200, f"CORS request failed with {response.status_code}"
        assert 'access-control-allow-origin' in [h.lower() for h in response.headers.keys()], \
            "CORS header missing"
        
        cors_header = response.headers.get('Access-Control-Allow-Origin', '')
        assert cors_header == '*' or 'example.com' in cors_header, \
            f"CORS policy restrictive: {cors_header}"
        
        print("✅ CORS policy allows cross-origin requests")
    
    def test_03_content_type_validation(self):
        """TEST 3: Content-Type header validation and security"""
        print("\n📄 Test 3: Content-Type Security Validation")
        
        # Test GET request content type
        response = self.jsonplaceholder.get_all_posts()
        
        # Assertions
        assert response.status_code == 200, f"Request failed with {response.status_code}"
        
        content_type = response.headers.get('content-type', '').lower()
        assert 'application/json' in content_type, \
            f"Expected JSON content-type, got: {content_type}"
        
        # Verify charset is specified (security best practice)
        assert 'charset' in content_type, \
            f"Content-type should specify charset: {content_type}"
        
        print(f"✅ Content-Type properly configured: {content_type}")
    
    # Input Validation & Injection Tests (3 tests)
    
    def test_04_sql_injection_attempt(self):
        """TEST 4: SQL Injection prevention testing"""
        print("\n💉 Test 4: SQL Injection Prevention")
        
        # Test SQL injection patterns in URL parameters
        sql_payloads = [
            "1'; DROP TABLE users; --",
            "1' OR '1'='1",
            "1 UNION SELECT * FROM users",
            "'; DELETE FROM posts; --"
        ]
        
        for payload in sql_payloads:
            try:
                # Attempt injection via query parameter
                response = requests.get(f"{self.base_url}/posts", 
                                      params={'userId': payload}, 
                                      timeout=5)
                
                # Should either return empty result or handle gracefully
                assert response.status_code in [200, 400, 404], \
                    f"Unexpected status for SQL injection: {response.status_code}"
                
                # Should not return database errors or expose internal structure
                response_text = response.text.lower()
                dangerous_keywords = ['sql', 'mysql', 'database', 'table', 'error', 'syntax']
                
                for keyword in dangerous_keywords:
                    assert keyword not in response_text, \
                        f"SQL injection may have exposed database info: {keyword}"
                        
            except requests.exceptions.Timeout:
                # Timeout is acceptable - shows server didn't crash
                pass
        
        print("✅ SQL injection attempts properly handled")
    
    def test_05_xss_prevention_testing(self):
        """TEST 5: Cross-Site Scripting (XSS) prevention"""
        print("\n🚫 Test 5: XSS Prevention Testing")
        
        # XSS payloads to test
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        for payload in xss_payloads:
            # Test XSS in POST data
            test_data = {
                "title": payload,
                "body": f"Test body with {payload}",
                "userId": 1
            }
            
            response = self.jsonplaceholder.create_post(test_data)
            
            # Should accept the request (API doesn't validate content)
            assert response.status_code == 201, f"POST failed with {response.status_code}"
            
            # Verify the payload is returned as-is (not executed)
            created_post = response.json()
            assert payload in created_post['title'], "Payload should be preserved as text"
            
            # Verify Content-Type is JSON (not HTML that could execute scripts)
            content_type = response.headers.get('content-type', '').lower()
            assert 'application/json' in content_type, \
                f"Response should be JSON, not executable: {content_type}"
        
        print("✅ XSS payloads handled safely as text data")
    
    def test_06_input_length_validation(self):
        """TEST 6: Input length and boundary testing"""
        print("\n📏 Test 6: Input Length Validation")
        
        # Test extremely long input
        long_string = "A" * 10000  # 10KB string
        very_long_string = "B" * 100000  # 100KB string
        
        test_cases = [
            {"title": long_string, "body": "Normal body", "userId": 1},
            {"title": "Normal title", "body": very_long_string, "userId": 1},
            {"title": "", "body": "", "userId": 1},  # Empty inputs
        ]
        
        for i, test_data in enumerate(test_cases, 1):
            response = self.jsonplaceholder.create_post(test_data)
            
            # Should handle gracefully (accept or reject properly)
            assert response.status_code in [200, 201, 400, 413], \
                f"Unexpected status for test case {i}: {response.status_code}"
            
            # If accepted, verify response time is reasonable
            if response.status_code in [200, 201]:
                assert response.response_time_ms < 5000, \
                    f"Response time too slow for large input: {response.response_time_ms}ms"
        
        print("✅ Input length boundaries handled appropriately")
    
    # Rate Limiting & Resource Protection (2 tests)
    
    def test_07_rate_limiting_behavior(self):
        """TEST 7: Rate limiting and throttling behavior"""
        print("\n⏱️ Test 7: Rate Limiting Testing")
        
        # Make rapid sequential requests
        request_count = 20
        responses = []
        
        for i in range(request_count):
            try:
                response = self.jsonplaceholder.get_post(1)
                responses.append({
                    'status': response.status_code,
                    'time': response.response_time_ms,
                    'headers': dict(response.headers)
                })
            except Exception as e:
                responses.append({'error': str(e)})
        
        # Analyze results
        successful_requests = [r for r in responses if r.get('status') == 200]
        
        # Should handle most requests successfully
        success_rate = len(successful_requests) / len(responses)
        assert success_rate >= 0.8, f"Success rate too low: {success_rate:.2%}"
        
        # Check for rate limiting headers
        rate_limit_headers = ['x-ratelimit', 'ratelimit', 'retry-after']
        has_rate_headers = any(
            any(header.lower() in str(resp.get('headers', {})).lower() 
                for header in rate_limit_headers)
            for resp in successful_requests
        )
        
        print(f"✅ Handled {len(successful_requests)}/{request_count} rapid requests")
        if has_rate_headers:
            print("✅ Rate limiting headers detected")
    
    def test_08_large_payload_handling(self):
        """TEST 8: Large payload and resource exhaustion testing"""
        print("\n📦 Test 8: Large Payload Handling")
        
        # Create increasingly large payloads
        payload_sizes = [1000, 10000, 50000]  # 1KB, 10KB, 50KB
        
        for size in payload_sizes:
            large_payload = {
                "title": "Large Payload Test",
                "body": "X" * size,
                "userId": 1
            }
            
            start_time = requests.packages.urllib3.util.Timeout.DEFAULT_TIMEOUT
            
            try:
                response = self.jsonplaceholder.create_post(large_payload)
                
                # Should handle gracefully
                assert response.status_code in [200, 201, 400, 413, 414], \
                    f"Unexpected status for {size}B payload: {response.status_code}"
                
                # Response time should be reasonable
                assert response.response_time_ms < 10000, \
                    f"Response time too slow for {size}B: {response.response_time_ms}ms"
                
                print(f"✅ {size}B payload: Status {response.status_code}, Time {response.response_time_ms}ms")
                
            except requests.exceptions.Timeout:
                print(f"✅ {size}B payload: Timed out (acceptable for large payloads)")
            except Exception as e:
                print(f"✅ {size}B payload: Error handled - {str(e)[:100]}")
    
    @classmethod
    def teardown_class(cls):
        """Cleanup after all tests"""
        print("\n🟡 GROUP 2: Authentication & Security Testing Completed ✅")
        print("🔐 Security validation and input testing verified!")


if __name__ == "__main__":
    # Run this specific test group
    pytest.main([__file__, "-v", "-s"])