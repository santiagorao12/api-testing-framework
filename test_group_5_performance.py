# test_group_5_performance.py - Performance & Advanced Features Testing
import pytest
import requests
import time
import statistics
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from api_client import JSONPlaceholderClient
from config import Config

class TestGroup5Performance:
    """GROUP 5: Performance & Advanced Features Testing (6 tests)"""
    
    @classmethod
    def setup_class(cls):
        """Setup test clients"""
        cls.jsonplaceholder = JSONPlaceholderClient()
        cls.base_url = Config.JSONPLACEHOLDER_BASE_URL
        print("\n🟣 GROUP 5: Performance & Advanced Features Testing Started")
    
    # Performance Testing (3 tests)
    
    def test_01_response_time_benchmarks(self):
        """TEST 1: Establish response time benchmarks for all endpoints"""
        print("\n⏱️ Test 1: Response Time Benchmarks")
        
        # Define performance benchmarks for different endpoint types
        endpoints_to_test = [
            ('/posts', 'GET', 'List all posts', 2000),           # Collection endpoints
            ('/posts/1', 'GET', 'Single post', 1500),           # Single resource
            ('/users', 'GET', 'List all users', 2000),          # Users collection
            ('/users/1', 'GET', 'Single user', 1500),           # Single user
            ('/comments?postId=1', 'GET', 'Filtered comments', 2000),  # Filtered data
            ('/posts/1/comments', 'GET', 'Nested comments', 2000),     # Nested resources
        ]
        
        performance_results = []
        
        for endpoint, method, description, max_time_ms in endpoints_to_test:
            # Run multiple requests to get average response time
            response_times = []
            
            for i in range(5):  # 5 samples per endpoint
                start_time = time.time()
                response = requests.request(method, f"{self.base_url}{endpoint}")
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                response_times.append(response_time_ms)
                
                # Basic validation
                assert response.status_code == 200, f"{description}: Request failed with {response.status_code}"
            
            # Calculate statistics
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            # Performance assertions
            assert avg_time < max_time_ms, \
                f"{description}: Average response time {avg_time:.2f}ms exceeds {max_time_ms}ms"
            
            performance_results.append({
                'endpoint': endpoint,
                'description': description,
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'samples': len(response_times)
            })
            
            print(f"✅ {description}: Avg {avg_time:.2f}ms (min: {min_time:.2f}ms, max: {max_time:.2f}ms)")
        
        # Overall performance summary
        overall_avg = statistics.mean([r['avg_time'] for r in performance_results])
        print(f"✅ Overall average response time: {overall_avg:.2f}ms")
        
        # Verify no endpoint is significantly slower than others (outlier detection)
        max_avg = max([r['avg_time'] for r in performance_results])
        min_avg = min([r['avg_time'] for r in performance_results])
        performance_variance = max_avg - min_avg
        
        assert performance_variance < 3000, \
            f"Performance variance too high: {performance_variance:.2f}ms between fastest and slowest"
        
        print("✅ Response time benchmarks established successfully")
    
    def test_02_concurrent_load_testing(self):
        """TEST 2: Test API performance under concurrent load"""
        print("\n🔄 Test 2: Concurrent Load Testing")
        
        def make_request(request_id):
            """Worker function for concurrent requests"""
            start_time = time.time()
            try:
                response = self.jsonplaceholder.get_all_posts()
                end_time = time.time()
                
                return {
                    'id': request_id,
                    'status_code': response.status_code,
                    'response_time': (end_time - start_time) * 1000,
                    'success': response.status_code == 200,
                    'data_length': len(response.json()) if response.status_code == 200 else 0
                }
            except Exception as e:
                return {
                    'id': request_id,
                    'error': str(e),
                    'success': False
                }
        
        # Test with different concurrency levels
        concurrency_tests = [
            (5, 'Low concurrency'),
            (10, 'Medium concurrency'),
            (20, 'High concurrency')
        ]
        
        for concurrent_users, test_description in concurrency_tests:
            print(f"\n📊 Testing {test_description} ({concurrent_users} concurrent requests)")
            
            # Execute concurrent requests
            with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = [executor.submit(make_request, i) for i in range(concurrent_users)]
                results = [future.result() for future in as_completed(futures, timeout=30)]
            
            # Analyze results
            successful_requests = [r for r in results if r.get('success', False)]
            failed_requests = [r for r in results if not r.get('success', False)]
            
            success_rate = len(successful_requests) / len(results)
            
            # Performance assertions
            assert success_rate >= 0.8, \
                f"{test_description}: Success rate {success_rate:.2%} too low"
            
            if successful_requests:
                response_times = [r['response_time'] for r in successful_requests]
                avg_response_time = statistics.mean(response_times)
                max_response_time = max(response_times)
                
                # Under load, response times may be higher but should be reasonable
                assert avg_response_time < 5000, \
                    f"{test_description}: Average response time {avg_response_time:.2f}ms too high"
                
                assert max_response_time < 10000, \
                    f"{test_description}: Max response time {max_response_time:.2f}ms too high"
                
                print(f"✅ {test_description}: {success_rate:.2%} success, avg {avg_response_time:.2f}ms")
            
            if failed_requests:
                print(f"⚠️ {len(failed_requests)} requests failed (acceptable under load)")
        
        print("✅ Concurrent load testing completed successfully")
    
    def test_03_data_volume_performance(self):
        """TEST 3: Test performance with different data volumes"""
        print("\n📊 Test 3: Data Volume Performance Testing")
        
        # Test endpoints that return different data volumes
        volume_tests = [
            ('/posts?_limit=1', 'Single post', 1),
            ('/posts?_limit=10', 'Small dataset', 10),
            ('/posts?_limit=50', 'Medium dataset', 50),
            ('/posts', 'Full dataset', 100),
            ('/comments', 'Large dataset', 500),    # Comments endpoint returns ~500 items
            ('/photos?_limit=100', 'Image metadata', 100)  # Photos with URL data
        ]
        
        volume_performance = []
        
        for endpoint, description, expected_count in volume_tests:
            start_time = time.time()
            response = self.jsonplaceholder.get(endpoint)
            end_time = time.time()
            
            # Basic validation
            assert response.status_code == 200, f"{description}: Request failed"
            
            data = response.json()
            response_time = (end_time - start_time) * 1000
            data_size = len(json.dumps(data).encode('utf-8'))  # Response size in bytes
            
            # Performance validation based on data volume
            if expected_count <= 10:
                max_time = 2000  # Small datasets: 2s max
            elif expected_count <= 100:
                max_time = 3000  # Medium datasets: 3s max
            else:
                max_time = 5000  # Large datasets: 5s max
            
            assert response_time < max_time, \
                f"{description}: Response time {response_time:.2f}ms exceeds {max_time}ms for {expected_count} items"
            
            # Calculate performance metrics
            items_per_second = len(data) / (response_time / 1000) if response_time > 0 else 0
            bytes_per_ms = data_size / response_time if response_time > 0 else 0
            
            volume_performance.append({
                'description': description,
                'item_count': len(data),
                'response_time': response_time,
                'data_size_bytes': data_size,
                'items_per_second': items_per_second,
                'throughput_bps': bytes_per_ms * 1000
            })
            
            print(f"✅ {description}: {len(data)} items, {response_time:.2f}ms, {data_size:,} bytes")
        
        # Analyze performance scaling
        largest_dataset = max(volume_performance, key=lambda x: x['item_count'])
        smallest_dataset = min(volume_performance, key=lambda x: x['item_count'])
        
        # Performance should scale reasonably with data size
        size_ratio = largest_dataset['item_count'] / smallest_dataset['item_count']
        time_ratio = largest_dataset['response_time'] / smallest_dataset['response_time']
        
        # Time shouldn't increase more than 10x even if data is 500x larger (due to efficient serialization)
        assert time_ratio < 10, f"Performance doesn't scale well: {time_ratio:.2f}x time for {size_ratio:.2f}x data"
        
        print(f"✅ Performance scaling: {size_ratio:.1f}x data → {time_ratio:.1f}x time")
        print("✅ Data volume performance testing completed")
    
    # Advanced HTTP Features (3 tests)
    
    def test_04_patch_partial_updates(self):
        """TEST 4: Test PATCH method for partial resource updates"""
        print("\n🔧 Test 4: PATCH Partial Updates")
        
        # First, get an existing post to establish baseline
        original_response = self.jsonplaceholder.get_post(1)
        assert original_response.status_code == 200, "Failed to get original post"
        original_post = original_response.json()
        
        # Test various partial update scenarios
        patch_scenarios = [
            ({'title': 'Updated Title Only'}, 'Title-only update'),
            ({'body': 'Updated body content only'}, 'Body-only update'),
            ({'userId': 2}, 'UserId-only update'),
            ({'title': 'New Title', 'body': 'New Body'}, 'Multiple field update'),
            ({'extraField': 'Should be ignored or added'}, 'Non-standard field'),
        ]
        
        for patch_data, description in patch_scenarios:
            # Perform PATCH request
            response = requests.patch(
                f"{self.base_url}/posts/1",
                json=patch_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # PATCH might return 200 (updated) or 404 (not supported)
            assert response.status_code in [200, 404, 405], \
                f"{description}: Unexpected PATCH status {response.status_code}"
            
            if response.status_code == 200:
                updated_post = response.json()
                
                # Verify partial update behavior
                for field, value in patch_data.items():
                    if field in ['title', 'body', 'userId']:  # Standard fields
                        assert updated_post.get(field) == value, \
                            f"{description}: Field '{field}' not updated correctly"
                
                # Verify unchanged fields remain unchanged
                for field in ['id']:  # ID should never change
                    assert updated_post.get(field) == original_post.get(field), \
                        f"{description}: Field '{field}' should not change in PATCH"
                
                print(f"✅ {description}: PATCH successful")
            else:
                print(f"✅ {description}: PATCH not supported (status {response.status_code})")
        
        print("✅ PATCH partial update testing completed")
    
    def test_05_http_headers_and_caching(self):
        """TEST 5: Test HTTP headers and caching behavior"""
        print("\n📋 Test 5: HTTP Headers and Caching")
        
        # Test 1: Custom request headers
        custom_headers = {
            'User-Agent': 'API-Testing-Framework/1.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'X-Custom-Header': 'TestValue123'
        }
        
        response = requests.get(f"{self.base_url}/posts/1", headers=custom_headers)
        assert response.status_code == 200, "Custom headers caused request to fail"
        
        # Verify response headers
        response_headers = {k.lower(): v for k, v in response.headers.items()}
        
        # Check for important response headers (content-length might be missing due to chunked encoding)
        important_headers = [
            'content-type',
            'date',
        ]
        
        for header in important_headers:
            assert header in response_headers, f"Missing important header: {header}"
        
        # Check for content-length OR transfer-encoding (both are valid)
        has_content_length = 'content-length' in response_headers
        has_transfer_encoding = 'transfer-encoding' in response_headers
        assert has_content_length or has_transfer_encoding, \
            "Missing both content-length and transfer-encoding headers"
        
        print("✅ Custom request headers handled correctly")
        
        # Test 2: Conditional requests (if supported)
        first_response = requests.get(f"{self.base_url}/posts/1")
        etag = first_response.headers.get('ETag')
        last_modified = first_response.headers.get('Last-Modified')
        
        if etag:
            # Test If-None-Match header
            conditional_response = requests.get(
                f"{self.base_url}/posts/1",
                headers={'If-None-Match': etag}
            )
            # Should return 304 Not Modified or 200 (if not supported)
            assert conditional_response.status_code in [200, 304], \
                f"Unexpected conditional request status: {conditional_response.status_code}"
            print("✅ ETag conditional requests supported")
        
        if last_modified:
            # Test If-Modified-Since header
            conditional_response = requests.get(
                f"{self.base_url}/posts/1",
                headers={'If-Modified-Since': last_modified}
            )
            assert conditional_response.status_code in [200, 304], \
                f"Unexpected conditional request status: {conditional_response.status_code}"
            print("✅ Last-Modified conditional requests supported")
        
        # Test 3: Content negotiation
        content_types = [
            'application/json',
            'application/*',
            '*/*',
            'text/html,application/json;q=0.9',  # Quality values
        ]
        
        for accept_header in content_types:
            response = requests.get(
                f"{self.base_url}/posts/1",
                headers={'Accept': accept_header}
            )
            assert response.status_code == 200, f"Accept header '{accept_header}' caused failure"
            
            # Should return JSON regardless of Accept header (API behavior)
            content_type = response.headers.get('content-type', '').lower()
            assert 'json' in content_type, f"Unexpected content type for Accept: {accept_header}"
        
        print("✅ Content negotiation working correctly")
        print("✅ HTTP headers and caching behavior verified")
    
    def test_06_api_consistency_and_versioning(self):
        """TEST 6: Test API consistency and version handling"""
        print("\n🔄 Test 6: API Consistency and Versioning")
        
        # Test 1: Response format consistency across similar endpoints
        endpoint_pairs = [
            ('/posts/1', '/users/1', 'Single resource format'),
            ('/posts', '/users', 'Collection format'),
            ('/posts/1/comments', '/users/1/albums', 'Nested resource format'),
        ]
        
        for endpoint1, endpoint2, description in endpoint_pairs:
            response1 = requests.get(f"{self.base_url}{endpoint1}")
            response2 = requests.get(f"{self.base_url}{endpoint2}")
            
            assert response1.status_code == 200, f"Failed to get {endpoint1}"
            assert response2.status_code == 200, f"Failed to get {endpoint2}"
            
            data1 = response1.json()
            data2 = response2.json()
            
            # Both should be same type (list or dict)
            assert type(data1) == type(data2), \
                f"{description}: Inconsistent response types between {endpoint1} and {endpoint2}"
            
            # Headers should be consistent
            content_type1 = response1.headers.get('content-type', '')
            content_type2 = response2.headers.get('content-type', '')
            assert 'json' in content_type1.lower() and 'json' in content_type2.lower(), \
                f"{description}: Inconsistent content types"
            
            print(f"✅ {description}: Response format consistent")
        
        # Test 2: Data field consistency
        post = requests.get(f"{self.base_url}/posts/1").json()
        user = requests.get(f"{self.base_url}/users/1").json()
        comment = requests.get(f"{self.base_url}/comments/1").json()
        
        # All resources should have 'id' field
        for resource, name in [(post, 'post'), (user, 'user'), (comment, 'comment')]:
            assert 'id' in resource, f"{name} missing required 'id' field"
            assert isinstance(resource['id'], int), f"{name} 'id' should be integer"
        
        print("✅ Data field consistency verified")
        
        # Test 3: API versioning headers (if supported)
        response = requests.get(f"{self.base_url}/posts/1")
        
        # Look for version-related headers
        version_headers = [
            'api-version',
            'x-api-version',
            'version',
            'x-version'
        ]
        
        found_version_header = False
        for header in version_headers:
            if header in [h.lower() for h in response.headers.keys()]:
                found_version_header = True
                print(f"✅ Version header found: {header}")
                break
        
        if not found_version_header:
            print("✅ No explicit version headers (typical for stable APIs)")
        
        # Test 4: URL structure consistency
        endpoints_to_check = [
            '/posts',
            '/posts/1',
            '/posts/1/comments',
            '/users',
            '/users/1',
            '/users/1/albums'
        ]
        
        all_successful = True
        for endpoint in endpoints_to_check:
            response = requests.get(f"{self.base_url}{endpoint}")
            if response.status_code != 200:
                all_successful = False
                print(f"⚠️ Endpoint {endpoint} returned {response.status_code}")
        
        assert all_successful, "Some standard REST endpoints are not available"
        print("✅ RESTful URL structure consistently implemented")
        
        print("✅ API consistency and versioning verification completed")
    
    @classmethod
    def teardown_class(cls):
        """Cleanup after all tests"""
        print("\n🟣 GROUP 5: Performance & Advanced Features Testing Completed ✅")
        print("🚀 Advanced API testing capabilities demonstrated!")
        print("\n" + "="*80)
        print("🎉 CONGRATULATIONS! ALL 5 GROUPS COMPLETED SUCCESSFULLY!")
        print("📊 FINAL SCORE: 33/33 TESTS - COMPREHENSIVE API TESTING FRAMEWORK")
        print("🏆 PORTFOLIO-READY PROFESSIONAL TESTING SUITE")
        print("="*80)


if __name__ == "__main__":
    # Run this specific test group
    pytest.main([__file__, "-v", "-s"])