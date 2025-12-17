# Services layer for the application
# This layer abstracts API calls and handles authorization

from .auth_service import AuthService
from .api_service import APIService

# Initialize services
auth_service = AuthService()
api_service = APIService()