# test_group_3_relationships.py - Data Relationships & Filtering Testing
import pytest
import requests
from api_client import JSONPlaceholderClient
from config import Config

class TestGroup3DataRelationships:
    """GROUP 3: Data Relationships & Filtering Testing (7 tests)"""
    
    @classmethod
    def setup_class(cls):
        """Setup test clients"""
        cls.jsonplaceholder = JSONPlaceholderClient()
        cls.base_url = Config.JSONPLACEHOLDER_BASE_URL
        print("\n🟠 GROUP 3: Data Relationships & Filtering Testing Started")
    
    # Nested Resources & Relationships (3 tests)
    
    def test_01_posts_comments_relationship(self):
        """TEST 1: Verify posts-comments relationship integrity"""
        print("\n🔗 Test 1: Posts-Comments Relationship")
        
        # Get a specific post
        post_response = self.jsonplaceholder.get_post(1)
        assert post_response.status_code == 200, f"Failed to get post: {post_response.status_code}"
        post_data = post_response.json()
        
        # Get comments for this post via nested route
        comments_response = self.jsonplaceholder.get_post_comments(1)
        assert comments_response.status_code == 200, f"Failed to get comments: {comments_response.status_code}"
        comments = comments_response.json()
        
        # Assertions
        assert len(comments) > 0, "Post should have comments"
        
        # Verify all comments belong to this post
        for comment in comments:
            assert comment['postId'] == post_data['id'], \
                f"Comment {comment['id']} belongs to post {comment['postId']}, not {post_data['id']}"
            
            # Verify comment structure
            required_fields = ['id', 'name', 'email', 'body', 'postId']
            for field in required_fields:
                assert field in comment, f"Comment missing field: {field}"
            
            # Verify email format in comments
            assert '@' in comment['email'], f"Invalid email format: {comment['email']}"
        
        print(f"✅ Post {post_data['id']} has {len(comments)} comments, all relationships valid")
    
    def test_02_users_posts_relationship(self):
        """TEST 2: Verify users-posts relationship integrity"""
        print("\n👤 Test 2: Users-Posts Relationship")
        
        # Get a specific user
        user_response = self.jsonplaceholder.get('/users/1')
        assert user_response.status_code == 200, f"Failed to get user: {user_response.status_code}"
        user_data = user_response.json()
        
        # Get posts by this user
        posts_response = self.jsonplaceholder.get_posts_by_user(1)
        assert posts_response.status_code == 200, f"Failed to get user posts: {posts_response.status_code}"
        posts = posts_response.json()
        
        # Assertions
        assert len(posts) > 0, f"User {user_data['id']} should have posts"
        
        # Verify all posts belong to this user
        for post in posts:
            assert post['userId'] == user_data['id'], \
                f"Post {post['id']} belongs to user {post['userId']}, not {user_data['id']}"
            
            # Verify post structure
            required_fields = ['id', 'title', 'body', 'userId']
            for field in required_fields:
                assert field in post, f"Post missing field: {field}"
            
            # Verify content is not empty
            assert len(post['title'].strip()) > 0, f"Post {post['id']} has empty title"
            assert len(post['body'].strip()) > 0, f"Post {post['id']} has empty body"
        
        print(f"✅ User {user_data['name']} has {len(posts)} posts, all relationships valid")
    
    def test_03_users_albums_photos_hierarchy(self):
        """TEST 3: Verify users-albums-photos three-level relationship"""
        print("\n📸 Test 3: Users-Albums-Photos Hierarchy")
        
        # Get user albums
        albums_response = self.jsonplaceholder.get('/users/1/albums')
        assert albums_response.status_code == 200, f"Failed to get user albums: {albums_response.status_code}"
        albums = albums_response.json()
        
        assert len(albums) > 0, "User should have albums"
        
        # Test first album's photos
        first_album = albums[0]
        photos_response = self.jsonplaceholder.get(f'/albums/{first_album["id"]}/photos')
        assert photos_response.status_code == 200, f"Failed to get album photos: {photos_response.status_code}"
        photos = photos_response.json()
        
        # Assertions
        assert len(photos) > 0, f"Album {first_album['id']} should have photos"
        
        for photo in photos:
            assert photo['albumId'] == first_album['id'], \
                f"Photo {photo['id']} belongs to album {photo['albumId']}, not {first_album['id']}"
            
            # Verify photo structure
            required_fields = ['id', 'title', 'url', 'thumbnailUrl', 'albumId']
            for field in required_fields:
                assert field in photo, f"Photo missing field: {field}"
            
            # Verify URLs are valid format
            assert photo['url'].startswith('http'), f"Invalid photo URL: {photo['url']}"
            assert photo['thumbnailUrl'].startswith('http'), f"Invalid thumbnail URL: {photo['thumbnailUrl']}"
        
        print(f"✅ User → Album {first_album['id']} → {len(photos)} photos, hierarchy valid")
    
    # Query Parameter Filtering (3 tests)
    
    def test_04_filter_posts_by_user(self):
        """TEST 4: Filter posts by userId parameter"""
        print("\n🔍 Test 4: Filter Posts by User ID")
        
        # Test filtering for multiple users
        test_user_ids = [1, 2, 3]
        
        for user_id in test_user_ids:
            response = self.jsonplaceholder.get_posts_by_user(user_id)
            assert response.status_code == 200, f"Failed to filter posts for user {user_id}"
            
            posts = response.json()
            assert len(posts) > 0, f"User {user_id} should have posts"
            
            # Verify all posts belong to requested user
            for post in posts:
                assert post['userId'] == user_id, \
                    f"Filter failed: Post {post['id']} belongs to user {post['userId']}, not {user_id}"
            
            print(f"✅ User {user_id}: Found {len(posts)} posts")
        
        # Test non-existent user
        response = self.jsonplaceholder.get_posts_by_user(999)
        assert response.status_code == 200, "Should handle non-existent user gracefully"
        posts = response.json()
        assert len(posts) == 0, "Non-existent user should have no posts"
        
        print("✅ Filtering by userId works correctly")
    
    def test_05_filter_comments_by_post(self):
        """TEST 5: Filter comments by postId parameter"""
        print("\n💬 Test 5: Filter Comments by Post ID")
        
        # Test filtering comments for multiple posts
        test_post_ids = [1, 2, 3]
        
        for post_id in test_post_ids:
            # Method 1: Query parameter filtering
            response = self.jsonplaceholder.get('/comments', params={'postId': post_id})
            assert response.status_code == 200, f"Failed to filter comments for post {post_id}"
            
            comments = response.json()
            assert len(comments) > 0, f"Post {post_id} should have comments"
            
            # Verify all comments belong to requested post
            for comment in comments:
                assert comment['postId'] == post_id, \
                    f"Filter failed: Comment {comment['id']} belongs to post {comment['postId']}, not {post_id}"
            
            # Method 2: Nested route (should return same results)
            nested_response = self.jsonplaceholder.get_post_comments(post_id)
            nested_comments = nested_response.json()
            
            # Both methods should return same data
            assert len(comments) == len(nested_comments), \
                f"Query filter and nested route returned different counts for post {post_id}"
            
            print(f"✅ Post {post_id}: Found {len(comments)} comments (both methods)")
        
        print("✅ Comment filtering by postId works correctly")
    
    def test_06_pagination_and_limits(self):
        """TEST 6: Test pagination and limit parameters"""
        print("\n📄 Test 6: Pagination and Limits")
        
        # Test limit parameter
        limit_tests = [5, 10, 20]
        
        for limit in limit_tests:
            response = self.jsonplaceholder.get('/posts', params={'_limit': limit})
            assert response.status_code == 200, f"Failed to get posts with limit {limit}"
            
            posts = response.json()
            assert len(posts) == limit, f"Expected {limit} posts, got {len(posts)}"
            
            # Verify posts are in correct order (should be first N posts)
            for i, post in enumerate(posts):
                expected_id = i + 1
                assert post['id'] == expected_id, f"Post order incorrect: got ID {post['id']}, expected {expected_id}"
        
        # Test start parameter (offset)
        start_offset = 10
        limit = 5
        response = self.jsonplaceholder.get('/posts', params={'_start': start_offset, '_limit': limit})
        assert response.status_code == 200, f"Failed to get posts with start {start_offset}"
        
        posts = response.json()
        assert len(posts) == limit, f"Expected {limit} posts with offset, got {len(posts)}"
        
        # Verify correct offset
        first_post_id = posts[0]['id']
        expected_first_id = start_offset + 1
        assert first_post_id == expected_first_id, \
            f"Offset incorrect: first post ID {first_post_id}, expected {expected_first_id}"
        
        print(f"✅ Pagination: _limit and _start parameters work correctly")
    
    def test_07_search_and_complex_filtering(self):
        """TEST 7: Advanced search and complex filtering scenarios"""
        print("\n🔎 Test 7: Advanced Search and Filtering")
        
        # Test 1: Multiple parameter filtering
        response = self.jsonplaceholder.get('/posts', params={
            'userId': 1,
            '_limit': 3
        })
        assert response.status_code == 200, "Multi-parameter filtering failed"
        posts = response.json()
        
        assert len(posts) == 3, f"Expected 3 posts, got {len(posts)}"
        for post in posts:
            assert post['userId'] == 1, f"Multi-filter failed: post {post['id']} not from user 1"
        
        # Test 2: Filter todos by completion status
        response = self.jsonplaceholder.get('/todos', params={'completed': 'true'})
        assert response.status_code == 200, "Boolean filtering failed"
        completed_todos = response.json()
        
        assert len(completed_todos) > 0, "Should find completed todos"
        for todo in completed_todos[:5]:  # Check first 5
            assert todo['completed'] == True, f"Todo {todo['id']} should be completed"
        
        # Test 3: Filter todos by user and completion
        response = self.jsonplaceholder.get('/todos', params={
            'userId': 1,
            'completed': 'false',
            '_limit': 5
        })
        assert response.status_code == 200, "Complex filtering failed"
        user_incomplete_todos = response.json()
        
        for todo in user_incomplete_todos:
            assert todo['userId'] == 1, f"Todo {todo['id']} not from user 1"
            assert todo['completed'] == False, f"Todo {todo['id']} should be incomplete"
        
        # Test 4: Invalid parameter handling
        response = self.jsonplaceholder.get('/posts', params={'invalidParam': 'test'})
        assert response.status_code == 200, "Should handle invalid parameters gracefully"
        # Should return all posts (ignore invalid parameter)
        posts = response.json()
        assert len(posts) == 100, "Invalid parameter should be ignored"
        
        print("✅ Advanced filtering and search functionality verified")
    
    @classmethod
    def teardown_class(cls):
        """Cleanup after all tests"""
        print("\n🟠 GROUP 3: Data Relationships & Filtering Testing Completed ✅")
        print("🔗 Data integrity and advanced querying capabilities verified!")


if __name__ == "__main__":
    # Run this specific test group
    pytest.main([__file__, "-v", "-s"])