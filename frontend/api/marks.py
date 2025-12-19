from typing import Optional, Any, List

from .dtos import *
import requests


class MarksAPI:
    """Marks API client with token per method."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def _make_request(self, method: str, endpoint: str, token: Optional[str] = None, **kwargs) -> Any:
        """Make an API request with optional token."""
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

    def get_task_marks(self, task_id: int, token: str) -> List[Dict[str, Any]]:
        """Get marks for a task."""
        response = self._make_request("GET", f"/api/tasks/{task_id}/marks", token=token)
        return response

    def create_mark(self, task_id: int, description: str, rate: Optional[int], token: str) -> Dict[str, Any]:
        """Create a mark for a task."""
        payload = {"Description": description, "Rate": rate, "TargetTask": task_id}
        response = self._make_request("POST", f"/api/tasks/{task_id}/marks", token=token, json=payload)
        return response

    def update_mark(self, mark_id: int, description: Optional[str], rate: Optional[int], token: str) -> Dict[str, Any]:
        """Update a mark."""
        payload: Dict[str, Any] = {}
        if description is not None:
            payload["Description"] = description
        if rate is not None:
            payload["Rate"] = rate
        response = self._make_request("PUT", f"/api/marks/{mark_id}", token=token, json=payload)
        return response

    def delete_mark(self, mark_id: int, token: str) -> APIResponse:
        """Delete a mark."""
        response = self._make_request("DELETE", f"/api/marks/{mark_id}", token=token)
        return APIResponse(**response)


marks_api = MarksAPI()


