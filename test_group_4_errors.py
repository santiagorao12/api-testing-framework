# test_group_4_errors.py - Error Handling & Edge Cases Testing
import pytest
import requests
import json
from api_client import JSONPlaceholderClient
from config import Config

class TestGroup4ErrorHandling:
    """GROUP 4: Error Handling & Edge Cases Testing (6 tests)"""
    
    @classmethod
    def setup_class(cls):
        """Setup test clients"""
        cls.jsonplaceholder = JSONPlaceholderClient()
        cls.base_url = Config.JSONPLACEHOLDER_BASE_URL
        print("\n🔴 GROUP 4: Error Handling & Edge Cases Testing Started")
    
    # HTTP Status Code Validation (3 tests)
    
    def test_01_404_not_found_scenarios(self):
        """TEST 1: Verify 404 responses for non-existent resources"""
        print("\n🚫 Test 1: 404 Not Found Scenarios")
        
        # Test various non-existent resource scenarios
        not_found_scenarios = [
            ('/posts/999', 'Non-existent post ID'),
            ('/posts/0', 'Zero post ID'),
            ('/posts/-1', 'Negative post ID'),
            ('/users/999', 'Non-existent user ID'),
            ('/albums/999', 'Non-existent album ID'),
            ('/comments/999', 'Non-existent comment ID'),
            ('/todos/999', 'Non-existent todo ID'),
            ('/nonexistent', 'Invalid endpoint'),
            ('/posts/abc', 'Non-numeric ID'),
        ]
        
        for endpoint, description in not_found_scenarios:
            response = requests.get(f"{self.base_url}{endpoint}")
            
            # Should return 404 for non-existent resources
            assert response.status_code == 404, \
                f"{description}: Expected 404, got {response.status_code} for {endpoint}"
            
            # Verify response time is reasonable even for errors
            assert hasattr(response, 'elapsed'), "Response should have timing info"
            response_time_ms = response.elapsed.total_seconds() * 1000
            assert response_time_ms < 3000, \
                f"404 response too slow: {response_time_ms}ms for {endpoint}"
            
            print(f"✅ {description}: 404 returned correctly")
        
        print("✅ All 404 scenarios handled properly")
    
    def test_02_invalid_http_methods(self):
        """TEST 2: Test unsupported HTTP methods on endpoints"""
        print("\n❌ Test 2: Invalid HTTP Methods")
        
        # Test unsupported methods on different endpoints
        method_tests = [
            ('PATCH', '/posts', 'PATCH on collection'),
            ('HEAD', '/posts/1', 'HEAD method'),
            ('OPTIONS', '/posts/1', 'OPTIONS method'),
            ('TRACE', '/posts/1', 'TRACE method'),
        ]
        
        for method, endpoint, description in method_tests:
            try:
                response = requests.request(method, f"{self.base_url}{endpoint}")
                
                # Should either be allowed (200-299) or properly rejected (404, 405, 501)
                valid_status_codes = [200, 204, 404, 405, 501]
                assert response.status_code in valid_status_codes, \
                    f"{description}: Unexpected status {response.status_code}"
                
                if response.status_code == 405:
                    print(f"✅ {description}: 405 Method Not Allowed")
                elif response.status_code == 404:
                    print(f"✅ {description}: 404 Not Found (endpoint doesn't support method)")
                else:
                    print(f"✅ {description}: {response.status_code} (handled)")
                    
            except requests.exceptions.RequestException as e:
                # Connection errors are acceptable for unsupported methods
                print(f"✅ {description}: Connection rejected (acceptable)")
        
        print("✅ HTTP method validation working correctly")
    
    def test_03_malformed_request_validation(self):
        """TEST 3: Test handling of malformed requests"""
        print("\n🔧 Test 3: Malformed Request Validation")
        
        # Test 1: Invalid JSON in POST request
        invalid_json_payloads = [
            '{"title": "test", "body": "test", "userId": }',  # Missing value
            '{"title": "test", "body": "test" "userId": 1}',   # Missing comma
            '{"title": "test", "body": "test", "userId": 1',   # Missing closing brace
            '{title: "test", body: "test", userId: 1}',        # Unquoted keys
            '{"title": "test", "body": "test", "userId": "abc"}', # Invalid type
        ]
        
        for payload in invalid_json_payloads:
            try:
                response = requests.post(
                    f"{self.base_url}/posts",
                    data=payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                # Should handle gracefully (400 Bad Request, 500 Server Error, or successful parsing)
                assert response.status_code in [200, 201, 400, 422, 500], \
                    f"Unexpected status for malformed JSON: {response.status_code}"
                
                if response.status_code == 500:
                    print(f"✅ Malformed JSON: Server error (appropriate for invalid JSON)")
                elif response.status_code in [400, 422]:
                    print(f"✅ Malformed JSON: Client error (appropriate rejection)")
                else:
                    print(f"✅ Malformed JSON: Accepted/processed")
                
            except requests.exceptions.RequestException:
                # Request exceptions are acceptable for malformed data
                pass
        
        # Test 2: Missing Content-Type header
        response = requests.post(
            f"{self.base_url}/posts",
            data='{"title": "test", "body": "test", "userId": 1}'
            # No Content-Type header
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 201, 400, 415], \
            f"Missing Content-Type not handled properly: {response.status_code}"
        
        # Test 3: Wrong Content-Type header
        response = requests.post(
            f"{self.base_url}/posts",
            data='{"title": "test", "body": "test", "userId": 1}',
            headers={'Content-Type': 'text/plain'}
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 201, 400, 415], \
            f"Wrong Content-Type not handled properly: {response.status_code}"
        
        print("✅ Malformed request handling verified")
    
    # Data Validation & Edge Cases (3 tests)
    
    def test_04_boundary_value_testing(self):
        """TEST 4: Test boundary values and edge cases"""
        print("\n📊 Test 4: Boundary Value Testing")
        
        # Test 1: Extreme numeric values
        extreme_values = [
            {'userId': 0, 'description': 'Zero user ID'},
            {'userId': -1, 'description': 'Negative user ID'},
            {'userId': 999999, 'description': 'Very large user ID'},
            {'userId': 2147483647, 'description': 'Max 32-bit integer'},
            {'userId': -2147483648, 'description': 'Min 32-bit integer'},
        ]
        
        for test_case in extreme_values:
            post_data = {
                "title": "Boundary Test",
                "body": "Testing extreme values",
                "userId": test_case['userId']
            }
            
            response = self.jsonplaceholder.create_post(post_data)
            
            # Should handle gracefully (accept or reject properly)
            assert response.status_code in [200, 201, 400, 422], \
                f"{test_case['description']}: Unexpected status {response.status_code}"
            
            if response.status_code in [200, 201]:
                created_post = response.json()
                assert 'id' in created_post, f"{test_case['description']}: Missing ID in response"
                print(f"✅ {test_case['description']}: Accepted")
            else:
                print(f"✅ {test_case['description']}: Properly rejected")
        
        # Test 2: String length boundaries
        length_tests = [
            ('', 'Empty string'),
            ('a', 'Single character'),
            ('a' * 1000, '1000 characters'),
            ('a' * 10000, '10000 characters'),
        ]
        
        for test_string, description in length_tests:
            post_data = {
                "title": test_string,
                "body": "Test body",
                "userId": 1
            }
            
            response = self.jsonplaceholder.create_post(post_data)
            assert response.status_code in [200, 201, 400, 413], \
                f"{description}: Unexpected status {response.status_code}"
            
            print(f"✅ {description}: Handled appropriately")
        
        print("✅ Boundary value testing completed")
    
    def test_05_special_characters_handling(self):
        """TEST 5: Test handling of special characters and encoding"""
        print("\n🔤 Test 5: Special Characters Handling")
        
        # Test various special character scenarios
        special_char_tests = [
            ('Unicode: 你好世界 🌍', 'Unicode and emoji'),
            ('HTML: <script>alert("test")</script>', 'HTML/Script tags'),
            ('SQL: \'; DROP TABLE posts; --', 'SQL injection characters'),
            ('Quotes: "test" \'test\' `test`', 'Various quote types'),
            ('Symbols: !@#$%^&*()_+-=[]{}|;:,.<>?', 'Special symbols'),
            ('Newlines:\nLine 1\nLine 2\r\nLine 3', 'Line breaks'),
            ('Tabs:\t\tIndented text', 'Tab characters'),
            ('Null bytes: test\x00test', 'Null bytes'),
        ]
        
        for test_content, description in special_char_tests:
            post_data = {
                "title": f"Special Chars Test: {description}",
                "body": test_content,
                "userId": 1
            }
            
            try:
                response = self.jsonplaceholder.create_post(post_data)
                
                # Should handle gracefully
                assert response.status_code in [200, 201, 400], \
                    f"{description}: Unexpected status {response.status_code}"
                
                if response.status_code in [200, 201]:
                    created_post = response.json()
                    # Verify content is preserved or properly sanitized
                    assert 'body' in created_post, f"{description}: Missing body in response"
                    print(f"✅ {description}: Content handled properly")
                else:
                    print(f"✅ {description}: Properly rejected")
                    
            except (UnicodeError, requests.exceptions.RequestException) as e:
                print(f"✅ {description}: Encoding error handled - {str(e)[:50]}")
        
        print("✅ Special character handling verified")
    
    def test_06_concurrent_request_conflicts(self):
        """TEST 6: Test handling of concurrent requests and potential conflicts"""
        print("\n⚡ Test 6: Concurrent Request Handling")
        
        import threading
        import time
        
        # Test 1: Rapid sequential requests
        rapid_responses = []
        start_time = time.time()
        
        for i in range(10):
            try:
                response = self.jsonplaceholder.get_post(1)
                rapid_responses.append({
                    'status': response.status_code,
                    'time': time.time() - start_time,
                    'response_time': getattr(response, 'response_time_ms', 0)
                })
            except Exception as e:
                rapid_responses.append({'error': str(e)})
        
        # Analyze rapid request results
        successful_rapid = [r for r in rapid_responses if r.get('status') == 200]
        success_rate = len(successful_rapid) / len(rapid_responses)
        
        assert success_rate >= 0.8, f"Rapid request success rate too low: {success_rate:.2%}"
        print(f"✅ Rapid requests: {len(successful_rapid)}/10 successful")
        
        # Test 2: Concurrent POST requests
        def create_post_worker(results, index):
            try:
                post_data = {
                    "title": f"Concurrent Test Post {index}",
                    "body": f"Created by thread {index}",
                    "userId": 1
                }
                response = self.jsonplaceholder.create_post(post_data)
                results.append({
                    'thread': index,
                    'status': response.status_code,
                    'id': response.json().get('id', None) if response.status_code in [200, 201] else None
                })
            except Exception as e:
                results.append({'thread': index, 'error': str(e)})
        
        # Create multiple threads for concurrent requests
        concurrent_results = []
        threads = []
        
        for i in range(5):
            thread = threading.Thread(target=create_post_worker, args=(concurrent_results, i))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # Analyze concurrent results
        successful_concurrent = [r for r in concurrent_results if r.get('status') in [200, 201]]
        concurrent_success_rate = len(successful_concurrent) / len(concurrent_results)
        
        assert concurrent_success_rate >= 0.6, \
            f"Concurrent request success rate too low: {concurrent_success_rate:.2%}"
        
        print(f"✅ Concurrent requests: {len(successful_concurrent)}/5 successful")
        
        # Test 3: Mixed operation stress test
        mixed_responses = []
        operations = [
            lambda: self.jsonplaceholder.get_all_posts(),
            lambda: self.jsonplaceholder.get_post(1),
            lambda: self.jsonplaceholder.create_post({"title": "Stress", "body": "Test", "userId": 1}),
            lambda: self.jsonplaceholder.get('/users'),
            lambda: self.jsonplaceholder.get('/comments?postId=1'),
        ]
        
        for operation in operations:
            try:
                response = operation()
                mixed_responses.append(response.status_code)
            except Exception as e:
                mixed_responses.append(f"Error: {str(e)[:30]}")
        
        successful_mixed = [r for r in mixed_responses if isinstance(r, int) and r in [200, 201]]
        mixed_success_rate = len(successful_mixed) / len(mixed_responses)
        
        assert mixed_success_rate >= 0.8, f"Mixed operations success rate too low: {mixed_success_rate:.2%}"
        print(f"✅ Mixed operations: {len(successful_mixed)}/5 successful")
        
        print("✅ Concurrent request handling verified")
    
    @classmethod
    def teardown_class(cls):
        """Cleanup after all tests"""
        print("\n🔴 GROUP 4: Error Handling & Edge Cases Testing Completed ✅")
        print("💥 Negative testing and edge case validation verified!")


if __name__ == "__main__":
    # Run this specific test group
    pytest.main([__file__, "-v", "-s"])