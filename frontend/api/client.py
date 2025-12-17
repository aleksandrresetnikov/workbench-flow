from typing import Any

from .auth import auth_api
from .users import users_api
from .projects import projects_api
from .task_groups import task_groups_api
from .tasks import tasks_api
from .files import files_api

class APIClient:
    """Main API client that combines all specific API clients"""
    
    def __init__(self):
        self.auth = auth_api
        self.users = users_api
        self.projects = projects_api
        self.task_groups = task_groups_api
        self.tasks = tasks_api
        self.files = files_api
    
    def health_check(self) -> Any:
        """Check API health"""
        import requests
        try:
            response = requests.get(f"{auth_api.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Health check failed: {e}")
            raise

# Singleton instance of the main API client
api_client = APIClient()