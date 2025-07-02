# api_client.py - Reusable API Client
import requests
import json
import time
from typing import Dict, Any, Optional
from config import Config

class APIClient:
    """Base API Client for making HTTP requests"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request and measure response time"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            response = self.session.request(method, url, timeout=Config.RESPONSE_TIMEOUT, **kwargs)
            end_time = time.time()
            response.response_time_ms = round((end_time - start_time) * 1000, 2)
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """GET request"""
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """POST request"""
        json_data = json.dumps(data) if data else None
        return self._make_request('POST', endpoint, data=json_data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """PUT request"""
        json_data = json.dumps(data) if data else None
        return self._make_request('PUT', endpoint, data=json_data)
    
    def patch(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """PATCH request"""
        json_data = json.dumps(data) if data else None
        return self._make_request('PATCH', endpoint, data=json_data)
    
    def delete(self, endpoint: str) -> requests.Response:
        """DELETE request"""
        return self._make_request('DELETE', endpoint)
    
    def set_auth_token(self, token: str):
        """Set authorization token for requests"""
        self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def remove_auth_token(self):
        """Remove authorization token"""
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']


class JSONPlaceholderClient(APIClient):
    """JSONPlaceholder API specific client"""
    
    def __init__(self):
        super().__init__(Config.JSONPLACEHOLDER_BASE_URL)
    
    def get_all_posts(self):
        return self.get('/posts')
    
    def get_post(self, post_id: int):
        return self.get(f'/posts/{post_id}')
    
    def create_post(self, post_data: Dict):
        return self.post('/posts', post_data)
    
    def update_post(self, post_id: int, post_data: Dict):
        return self.put(f'/posts/{post_id}', post_data)
    
    def delete_post(self, post_id: int):
        return self.delete(f'/posts/{post_id}')
    
    def get_post_comments(self, post_id: int):
        return self.get(f'/posts/{post_id}/comments')
    
    def get_posts_by_user(self, user_id: int):
        return self.get('/posts', params={'userId': user_id})


class ReqResClient(APIClient):
    """ReqRes API specific client"""
    
    def __init__(self):
        super().__init__(Config.REQRES_BASE_URL)
        # ReqRes doesn't need special headers - remove content-type restriction
        self.session.headers.clear()
        self.session.headers.update({
            'Accept': 'application/json'
        })
    
    def get_users(self, page: int = 1):
        return self.get('/users', params={'page': page})
    
    def get_user(self, user_id: int):
        return self.get(f'/users/{user_id}')
    
    def create_user(self, user_data: Dict):
        # ReqRes accepts both JSON and form data, let's use JSON properly
        return self._make_request('POST', '/users', json=user_data)
    
    def update_user(self, user_id: int, user_data: Dict):
        return self._make_request('PUT', f'/users/{user_id}', json=user_data)
    
    def delete_user(self, user_id: int):
        return self.delete(f'/users/{user_id}')
    
    def login(self, credentials: Dict):
        return self._make_request('POST', '/login', json=credentials)
    
    def register(self, user_data: Dict):
        return self._make_request('POST', '/register', json=user_data)