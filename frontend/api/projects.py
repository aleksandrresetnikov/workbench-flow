from typing import Optional, Any, List
from .dtos import *
import requests

class ProjectsAPI:
    """Projects API client with token per method"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: float = 10.0):
        self.base_url = base_url
        self.timeout = timeout
        # Session to enable connection pooling and reduce latency on multiple requests
        self.session = requests.Session()
        # Avoid using environment proxy settings by default (can cause delays if misconfigured)
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
            try:
                response.raise_for_status()
                # try json, fallback to text
                try:
                    return response.json()
                except ValueError:
                    return response.text
            except requests.exceptions.HTTPError as http_err:
                # extract useful body to help debug validation errors
                body = None
                try:
                    body = response.json()
                except ValueError:
                    body = response.text
                print(f"API request failed: {http_err} - {body}")
                # raise a clearer exception for the UI to show
                raise Exception(f"{response.status_code} {body}") from http_err
        except requests.exceptions.RequestException as e:
            elapsed = time.monotonic() - start
            print(f"API request failed after {elapsed:.3f}s: {e}")
            raise
    
    def get_my_projects(self, token: str) -> List[ProjectDTO]:
        """Get my projects"""
        response = self._make_request("GET", "/api/projects/my", token=token)
        return [ProjectDTO(**project) for project in response]
    
    def get_all_projects(self, token: str) -> List[ProjectDTO]:
        """Get all projects"""
        response = self._make_request("GET", "/api/projects/", token=token)
        return [ProjectDTO(**project) for project in response]
    
    def get_project_details(self, project_id: int, token: str) -> ProjectWithDetailsDTO:
        """Get project details"""
        response = self._make_request("GET", f"/api/projects/{project_id}", token=token)
        return ProjectWithDetailsDTO(**response)
    
    def create_project(self, project_data: ProjectCreateDTO, token: str) -> ProjectDTO:
        """Create a new project"""
        response = self._make_request("POST", "/api/projects/", token=token, json=project_data.dict())
        return ProjectDTO(**response)
    
    def update_project(self, project_id: int, project_data: ProjectUpdateDTO, token: str) -> ProjectDTO:
        """Update a project"""
        response = self._make_request("PUT", f"/api/projects/{project_id}", token=token, json=project_data.dict(exclude_unset=True))
        return ProjectDTO(**response)
    
    def get_project_members(self, project_id: int, token: str) -> List[ProjectMemberWithUserDTO]:
        """Get project members"""
        response = self._make_request("GET", f"/api/projects/{project_id}/members", token=token)
        return [ProjectMemberWithUserDTO(**member) for member in response]
    
    def add_project_member(self, project_id: int, member_data: ProjectMemberCreateDTO, token: str) -> ProjectMemberDTO:
        """Add a member to project"""
        response = self._make_request("POST", f"/api/projects/{project_id}/members", token=token, json=member_data.dict(exclude_none=True))
        return ProjectMemberDTO(**response)
    
    def update_project_member_access(self, project_id: int, member_id: int, access_data: ProjectMemberBaseDTO, token: str) -> ProjectMemberDTO:
        """Update project member access level / assigned role"""
        response = self._make_request("PUT", f"/api/projects/{project_id}/members/{member_id}", token=token, json=access_data.dict(exclude_unset=True, exclude_none=True))
        return ProjectMemberDTO(**response)

    # ---- Project roles ----

    def get_project_roles(self, project_id: int, token: str) -> List[ProjectRoleDTO]:
        """Get project-defined roles (admin-only endpoint on backend)"""
        response = self._make_request("GET", f"/api/projects/{project_id}/roles", token=token)
        return [ProjectRoleDTO(**role) for role in response]

    def create_project_role(self, project_id: int, role_data: ProjectRoleCreateDTO, token: str) -> ProjectRoleDTO:
        """Create new role for project (admin-only)"""
        response = self._make_request("POST", f"/api/projects/{project_id}/roles", token=token, json=role_data.dict())
        return ProjectRoleDTO(**response)

    def update_project_role(self, role_id: int, role_data: ProjectRoleUpdateDTO, token: str) -> ProjectRoleDTO:
        """Update existing project role (admin-only)"""
        response = self._make_request("PUT", f"/api/roles/{role_id}", token=token, json=role_data.dict(exclude_unset=True))
        return ProjectRoleDTO(**response)

    def delete_project_role(self, role_id: int, token: str) -> APIResponse:
        """Delete project role (admin-only)"""
        response = self._make_request("DELETE", f"/api/roles/{role_id}", token=token)
        return APIResponse(**response)
    
    def remove_project_member(self, project_id: int, member_id: int, token: str) -> APIResponse:
        """Remove project member"""
        response = self._make_request("DELETE", f"/api/projects/{project_id}/members/{member_id}", token=token)
        return APIResponse(**response)

# Singleton instance
projects_api = ProjectsAPI()