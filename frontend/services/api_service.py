# API Service
# Handles general API calls with authorization headers

from typing import Optional, Dict, Any
from api.client import api_client

class APIService:
    def __init__(self):
        pass

    def get(self, endpoint: str, token: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a GET request to the API"""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = api_client.get(endpoint, headers=headers, params=params)
        return response

    def post(self, endpoint: str, token: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make a POST request to the API"""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = api_client.post(endpoint, headers=headers, json=data)
        return response

    def put(self, endpoint: str, token: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make a PUT request to the API"""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = api_client.put(endpoint, headers=headers, json=data)
        return response

    def delete(self, endpoint: str, token: Optional[str] = None) -> Any:
        """Make a DELETE request to the API"""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = api_client.delete(endpoint, headers=headers)
        return response