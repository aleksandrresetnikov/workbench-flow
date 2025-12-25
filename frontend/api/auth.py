from typing import Optional, Any
from .dtos import *
import requests

class AuthAPI:
    """Auth API client with token per method"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: float = 10.0):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.trust_env = False
    
    def _make_request(self, method: str, endpoint: str, token: Optional[str] = None, **kwargs) -> Any:
        """Make an API request with optional token and timing/logging (includes DNS resolution diagnostics)"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # DNS resolution diagnostics
        from urllib.parse import urlparse
        import socket, time
        host = urlparse(url).hostname
        start_res = time.monotonic()
        try:
            addrs = socket.getaddrinfo(host, None)
            resolved_ips = {a[4][0] for a in addrs}
            res_elapsed = time.monotonic() - start_res
            print(f"[DNS] resolved {host} -> {resolved_ips} in {res_elapsed:.3f}s")
        except Exception as e:
            res_elapsed = time.monotonic() - start_res
            print(f"[DNS] resolution failed for {host} after {res_elapsed:.3f}s: {e}")

        import time
        start = time.monotonic()
        try:
            response = self.session.request(method, url, headers=headers, timeout=self.timeout, **kwargs)
            elapsed = time.monotonic() - start
            print(f"[API] {method} {url} completed in {elapsed:.3f}s")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            elapsed = time.monotonic() - start
            print(f"API request failed after {elapsed:.3f}s: {e}")
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