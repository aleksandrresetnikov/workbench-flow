from typing import Optional, Any, List
from .dtos import *
import requests

class TasksAPI:
    """Tasks API client with token per method"""
    
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
            # Try to return json payload, but fall back to raw text
            try:
                return response.json()
            except Exception:
                return response.text
        except requests.exceptions.RequestException as e:
            # If the response is available, include its body for better diagnostics (e.g., 422 validation errors)
            resp = getattr(e, 'response', None)
            detail = None
            if resp is not None:
                try:
                    detail = resp.json()
                except Exception:
                    detail = resp.text
            msg = f"API request failed: {e}"
            if detail is not None:
                msg = f"API request failed: {detail}"
            print(msg)
            raise Exception(msg) from e
    
    def get_tasks(self, project_id: int, token: str) -> List[TaskDTO]:
        """Get tasks for a project"""
        response = self._make_request("GET", f"/api/tasks/projects/{project_id}/tasks", token=token)
        return [TaskDTO(**task) for task in response]
    
    def create_task(self, project_id: int, task_data: TaskCreateDTO, token: str) -> TaskDTO:
        """Create a new task"""
        payload = task_data.dict(exclude_none=True)
        # ensure date objects are serialized
        if "DeadLine" in payload and payload["DeadLine"] is not None:
            dl = payload["DeadLine"]
            try:
                payload["DeadLine"] = dl.isoformat()
            except Exception:
                pass
        response = self._make_request("POST", f"/api/tasks/projects/{project_id}/tasks", token=token, json=payload)
        return TaskDTO(**response)

# Singleton instance
tasks_api = TasksAPI()