from typing import Optional, Any, List
from .dtos import *
import requests

class UsersAPI:
    """Users API client with token per method"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def _make_request(self, method: str, endpoint: str, token: Optional[str] = None, **kwargs) -> Any:
        """Make an API request with optional token"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            raise
    
    def get_users(self, token: str) -> List[UserDTO]:
        """Get all users"""
        response = self._make_request("GET", "/api/users/", token=token)
        return [UserDTO(**user) for user in response]
    
    def get_user(self, user_id: int, token: str) -> UserDTO:
        """Get a specific user"""
        response = self._make_request("GET", f"/api/users/{user_id}", token=token)
        return UserDTO(**response)
    
    def update_user(self, user_id: int, user_data: UserUpdateDTO, token: str) -> UserDTO:
        """Update a user"""
        response = self._make_request("PUT", f"/api/users/{user_id}", token=token, json=user_data.dict(exclude_unset=True))
        return UserDTO(**response)
    
    def delete_user(self, user_id: int, token: str) -> APIResponse:
        """Delete a user"""
        response = self._make_request("DELETE", f"/api/users/{user_id}", token=token)
        return APIResponse(**response)

# Singleton instance
users_api = UsersAPI()