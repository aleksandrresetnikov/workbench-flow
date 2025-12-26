from typing import Optional, Any, List
from .dtos import *
import requests

class TasksAPI:
    """Tasks API client with token per method"""
    
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
            # Try to return json payload, but fall back to raw text
            try:
                response.raise_for_status()
                try:
                    return response.json()
                except Exception:
                    return response.text
            except requests.exceptions.HTTPError as http_err:
                resp = getattr(http_err, 'response', None)
                detail = None
                if resp is not None:
                    try:
                        detail = resp.json()
                    except Exception:
                        detail = resp.text
                msg = f"API request failed: {detail or http_err}"
                print(msg)
                raise Exception(msg) from http_err
        except requests.exceptions.RequestException as e:
            elapsed = time.monotonic() - start
            print(f"API request failed after {elapsed:.3f}s: {e}")
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
            raise Exception(msg) from e
    
    def get_tasks(self, project_id: int, token: str) -> List[TaskDTO]:
        """Get tasks for a project"""
        response = self._make_request("GET", f"/api/tasks/projects/{project_id}/tasks", token=token)
        return [TaskDTO(**task) for task in response]
    
    def create_task(self, project_id: int, task_data: TaskCreateDTO, token: str) -> TaskDTO:
        """Create a new task in a project"""
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
    
    def update_task(self, task_id: int, task_data: TaskUpdateDTO, token: str) -> TaskDTO:
        """Update a task"""
        payload = task_data.dict(exclude_none=True)
        # ensure date objects are serialized
        if "DeadLine" in payload and payload["DeadLine"] is not None:
            dl = payload["DeadLine"]
            try:
                payload["DeadLine"] = dl.isoformat()
            except Exception:
                pass
        response = self._make_request("PUT", f"/api/tasks/{task_id}", token=token, json=payload)
        return TaskDTO(**response)

# Singleton instance
tasks_api = TasksAPI()