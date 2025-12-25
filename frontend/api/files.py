from typing import Optional, Any, List
from .dtos import *
import requests

class FilesAPI:
    """Files API client with token per method"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: float = 10.0):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.trust_env = False
    
    def _make_request(self, method: str, endpoint: str, token: Optional[str] = None, **kwargs) -> Any:
        """Make an API request with optional token and timing/logging"""
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
    
    def upload_file(self, project_id: int, file_path: str, token: str) -> FileDTO:
        """Upload a file"""
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = self._make_request("POST", f"/api/files/projects/{project_id}/files", token=token, files=files)
            return FileDTO(**response)
    
    def get_project_files(self, project_id: int, token: str) -> List[FileDTO]:
        """Get files for a project"""
        response = self._make_request("GET", f"/api/files/projects/{project_id}/files", token=token)
        return [FileDTO(**file) for file in response]

# Singleton instance
files_api = FilesAPI()