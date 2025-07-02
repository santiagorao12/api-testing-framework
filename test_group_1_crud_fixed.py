# test_group_1_crud_fixed.py - Basic CRUD Operations Tests (JSONPlaceholder Focus)
import pytest
import json
from api_client import JSONPlaceholderClient
from config import Config

class TestGroup1BasicCRUD:
    """GROUP 1: Basic CRUD Operations Testing (8 comprehensive tests)"""
    
    @classmethod
    def setup_class(cls):
        """Setup test clients"""
        cls.jsonplaceholder = JSONPlaceholderClient()
        print("\n🔵 GROUP 1: Basic CRUD Operations Testing Started")
    
    # Core CRUD Tests (5 tests)
    
    def test_01_get_all_posts(self):
        """TEST 1: GET /posts - List all posts (verify 100 posts)"""
        print("\n📋 Test 1: GET All Posts")
        
        response = self.jsonplaceholder.get_all_posts()
        
        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        posts = response.json()
        assert len(posts) == 100, f"Expected 100 posts, got {len(posts)}"
        
        # Verify response time
        assert response.response_time_ms < Config.MAX_RESPONSE_TIME, \
            f"Response time {response.response_time_ms}ms exceeds {Config.MAX_RESPONSE_TIME}ms"
        
        # Verify first post structure
        first_post = posts[0]
        required_fields = ['id', 'title', 'body', 'userId']
        for field in required_fields:
            assert field in first_post, f"Missing required field: {field}"
        
        print(f"✅ Found {len(posts)} posts, response time: {response.response_time_ms}ms")
    
    def test_02_get_single_post(self):
        """TEST 2: GET /posts/1 - Get single post (verify structure)"""
        print("\n📄 Test 2: GET Single Post")
        
        response = self.jsonplaceholder.get_post(1)
        
        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        post = response.json()
        assert post['id'] == 1, f"Expected post ID 1, got {post['id']}"
        assert 'title' in post and len(post['title']) > 0, "Post title is missing or empty"
        assert 'body' in post and len(post['body']) > 0, "Post body is missing or empty"
        assert 'userId' in post, "Post userId is missing"
        
        print(f"✅ Post ID: {post['id']}, Title: '{post['title'][:50]}...'")
    
    def test_03_create_new_post(self):
        """TEST 3: POST /posts - Create new post (verify response)"""
        print("\n➕ Test 3: CREATE New Post")
        
        response = self.jsonplaceholder.create_post(Config.TEST_POST_DATA)
        
        # Assertions
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        
        created_post = response.json()
        assert created_post['title'] == Config.TEST_POST_DATA['title'], "Title mismatch"
        assert created_post['body'] == Config.TEST_POST_DATA['body'], "Body mismatch"
        assert created_post['userId'] == Config.TEST_POST_DATA['userId'], "UserId mismatch"
        assert 'id' in created_post, "New post should have an ID"
        
        print(f"✅ Created post ID: {created_post['id']}")
    
    def test_04_update_post(self):
        """TEST 4: PUT /posts/1 - Update entire post (verify changes)"""
        print("\n✏️ Test 4: UPDATE Post")
        
        update_data = {
            "id": 1,
            "title": "Updated Test Title",
            "body": "Updated test body content",
            "userId": 1
        }
        
        response = self.jsonplaceholder.update_post(1, update_data)
        
        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        updated_post = response.json()
        assert updated_post['title'] == update_data['title'], "Title not updated"
        assert updated_post['body'] == update_data['body'], "Body not updated"
        assert updated_post['id'] == 1, "Post ID should remain 1"
        
        print(f"✅ Updated post title: '{updated_post['title']}'")
    
    def test_05_delete_post(self):
        """TEST 5: DELETE /posts/1 - Delete post (verify 200 status)"""
        print("\n🗑️ Test 5: DELETE Post")
        
        response = self.jsonplaceholder.delete_post(1)
        
        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        print("✅ Post deleted successfully")
    
    # Advanced JSONPlaceholder Tests (3 additional tests)
    
    def test_06_get_users(self):
        """TEST 6: GET /users - List all users (verify structure)"""
        print("\n👥 Test 6: GET All Users")
        
        response = self.jsonplaceholder.get('/users')
        
        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        users = response.json()
        assert len(users) == 10, f"Expected 10 users, got {len(users)}"
        
        # Verify user structure
        first_user = users[0]
        required_fields = ['id', 'name', 'username', 'email']
        for field in required_fields:
            assert field in first_user, f"Missing required field: {field}"
        
        print(f"✅ Found {len(users)} users")
    
    def test_07_get_post_comments(self):
        """TEST 7: GET /posts/1/comments - Nested resource (verify comments)"""
        print("\n💬 Test 7: GET Post Comments")
        
        response = self.jsonplaceholder.get_post_comments(1)
        
        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        comments = response.json()
        assert len(comments) == 5, f"Expected 5 comments for post 1, got {len(comments)}"
        
        # Verify comment structure
        first_comment = comments[0]
        required_fields = ['id', 'name', 'email', 'body', 'postId']
        for field in required_fields:
            assert field in first_comment, f"Missing required field: {field}"
        
        assert first_comment['postId'] == 1, "Comment should belong to post 1"
        
        print(f"✅ Found {len(comments)} comments for post 1")
    
    def test_08_filter_posts_by_user(self):
        """TEST 8: GET /posts?userId=1 - Filter posts by user (verify filtering)"""
        print("\n🔍 Test 8: Filter Posts by User")
        
        response = self.jsonplaceholder.get_posts_by_user(1)
        
        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        posts = response.json()
        assert len(posts) == 10, f"Expected 10 posts for user 1, got {len(posts)}"
        
        # Verify all posts belong to user 1
        for post in posts:
            assert post['userId'] == 1, f"Post {post['id']} belongs to user {post['userId']}, not 1"
        
        print(f"✅ Found {len(posts)} posts for user 1")
    
    @classmethod
    def teardown_class(cls):
        """Cleanup after all tests"""
        print("\n🔵 GROUP 1: Basic CRUD Operations Testing Completed ✅")
        print("🎯 All JSONPlaceholder API operations verified successfully!")


if __name__ == "__main__":
    # Run this specific test group
    pytest.main([__file__, "-v", "-s"])