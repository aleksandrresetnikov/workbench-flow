#!/usr/bin/env python3

"""
Test script for the new project management API endpoints.
This script tests the main functionality of the project management API.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, SessionLocal
from app.models import Base
from app import models
from datetime import datetime

def get_test_db():
    """Create a test database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the dependency to use test database
app.dependency_overrides[get_db] = get_test_db

client = TestClient(app)

def test_project_management_api():
    """Test the project management API endpoints"""
    
    print("Testing Project Management API...")
    
    # Test 1: Create a new project
    print("\n1. Testing project creation...")
    response = client.post(
        "/projects/",
        json={
            "Name": "Test Project",
            "Description": "This is a test project"
        },
        headers={"Authorization": "Bearer test_token"}  # This would need a valid token in real testing
    )
    print(f"Create project response: {response.status_code} - {response.json()}")
    
    # Test 2: Get all projects
    print("\n2. Testing get all projects...")
    response = client.get(
        "/projects/",
        headers={"Authorization": "Bearer test_token"}
    )
    print(f"Get all projects response: {response.status_code} - {response.json()}")
    
    # Test 3: Get project details (assuming project with ID 1 exists)
    print("\n3. Testing get project details...")
    response = client.get(
        "/projects/1",
        headers={"Authorization": "Bearer test_token"}
    )
    print(f"Get project details response: {response.status_code} - {response.json()}")
    
    # Test 4: Update project
    print("\n4. Testing project update...")
    response = client.put(
        "/projects/1",
        json={
            "Name": "Updated Test Project",
            "Description": "This is an updated test project"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    print(f"Update project response: {response.status_code} - {response.json()}")
    
    # Test 5: Add project member
    print("\n5. Testing add project member...")
    response = client.post(
        "/projects/1/members",
        json={
            "MemnerId": 2,  # Assuming user with ID 2 exists
            "Role": "Admin"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    print(f"Add project member response: {response.status_code} - {response.json()}")
    
    # Test 6: Get project members
    print("\n6. Testing get project members...")
    response = client.get(
        "/projects/1/members",
        headers={"Authorization": "Bearer test_token"}
    )
    print(f"Get project members response: {response.status_code} - {response.json()}")
    
    # Test 7: Update project member role
    print("\n7. Testing update project member role...")
    response = client.put(
        "/projects/1/members/2",
        json={
            "Role": "Common"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    print(f"Update project member role response: {response.status_code} - {response.json()}")
    
    # Test 8: Remove project member
    print("\n8. Testing remove project member...")
    response = client.delete(
        "/projects/1/members/2",
        headers={"Authorization": "Bearer test_token"}
    )
    print(f"Remove project member response: {response.status_code} - {response.json()}")
    
    print("\nProject Management API testing completed!")

if __name__ == "__main__":
    test_project_management_api()