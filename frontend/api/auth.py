from typing import Optional, Any
from .dtos import *
import requests

class AuthAPI:
    """Auth API client with token per method"""
    
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
    
    def register_user(self, user_data: UserCreateDTO) -> Any:
        """Register a new user"""
        return self._make_request("POST", "/api/auth/register", json=user_data.dict())
    
    def confirm_otp(self, otp_data: OtpConfirmDTO) -> Any:
        """Confirm OTP code"""
        return self._make_request("PATCH", "/api/auth/confirm-otp", json=otp_data.dict())
    
    def resend_otp(self, email: str) -> Any:
        """Resend OTP code"""
        return self._make_request("POST", "/api/auth/again-otp", json={"email": email})
    
    def login(self, login_data: UserLoginDTO) -> TokenDTO:
        """Login and get access token"""
        response = self._make_request(
            "POST", 
            "/api/auth/login", 
            json=login_data.dict()
        )
        return TokenDTO(**response)
    
    def get_current_user(self, token: str) -> UserDTO:
        """Get current user information"""
        response = self._make_request("GET", "/api/auth/fetch", token=token)
        return UserDTO(**response)

# Singleton instance
auth_api = AuthAPI()