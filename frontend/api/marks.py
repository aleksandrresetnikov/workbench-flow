from typing import Optional, Any, List

from .dtos import *
import requests


class MarksAPI:
    """Marks API client with token per method."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: float = 10.0):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.trust_env = False

    def _make_request(self, method: str, endpoint: str, token: Optional[str] = None, **kwargs) -> Any:
        """Make an API request with optional token and timing/logging."""
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


