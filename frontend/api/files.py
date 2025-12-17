from typing import Optional, Any, List
from .dtos import *
import requests

class FilesAPI:
    """Files API client with token per method"""
    
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