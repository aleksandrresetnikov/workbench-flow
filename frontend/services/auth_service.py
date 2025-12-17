# Auth Service
# Handles authentication-related operations and token management

from typing import Optional
from api.auth import auth_api
from api.dtos import UserCreateDTO, UserLoginDTO, OtpConfirmDTO, TokenDTO, UserDTO

class AuthService:
    def __init__(self):
        self._token: Optional[str] = None
        self._current_user: Optional[UserDTO] = None

    @property
    def token(self) -> Optional[str]:
        return self._token

    @property
    def current_user(self) -> Optional[UserDTO]:
        return self._current_user

    def register_user(self, username: str, email: str, password: str) -> bool:
        """Register a new user"""
        user_data = UserCreateDTO(Username=username, Email=email, Password=password)
        try:
            auth_api.register_user(user_data)
            return True
        except Exception as e:
            print(f"Registration failed: {e}")
            return False

    def confirm_otp(self, email: str, code: str) -> bool:
        """Confirm OTP code"""
        otp_data = OtpConfirmDTO(email=email, code=code)
        try:
            auth_api.confirm_otp(otp_data)
            return True
        except Exception as e:
            print(f"OTP confirmation failed: {e}")
            return False

    def resend_otp(self, email: str) -> bool:
        """Resend OTP code"""
        try:
            auth_api.resend_otp(email)
            return True
        except Exception as e:
            print(f"OTP resend failed: {e}")
            return False

    def login(self, username: str, password: str) -> bool:
        """Login and store the token"""
        login_data = UserLoginDTO(username=username, password=password)
        try:
            token_data = auth_api.login(login_data)
            self._token = token_data.access_token
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def fetch_current_user(self) -> bool:
        """Fetch current user information using the stored token"""
        if not self._token:
            return False

        try:
            user_data = auth_api.get_current_user(self._token)
            self._current_user = user_data
            return True
        except Exception as e:
            print(f"Failed to fetch current user: {e}")
            self._token = None
            return False

    def logout(self):
        """Clear the stored token and user information"""
        self._token = None
        self._current_user = None