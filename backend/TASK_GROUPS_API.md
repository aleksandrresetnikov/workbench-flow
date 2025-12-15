# Task Groups API Documentation

This document describes the Task Groups API that has been implemented for managing task groups within projects.

## Overview

The Task Groups API provides endpoints for managing task groups that belong to specific projects. Each task group is associated with exactly one project, and all operations require proper authentication and project access.

## Base URL

All endpoints are available under the `/api` prefix.

## Endpoints

### 1. Get All Task Groups for a Project

**Endpoint:** `GET /api/projects/{project_id}/groups`

**Description:** Retrieves all task groups that belong to a specific project.

**Authentication:** Required (user must have access to the project)

**Parameters:**
- `project_id` (path parameter): The ID of the project

**Response:**
- `200 OK`: Array of task group objects
- `403 Forbidden`: User doesn't have access to the project
- `404 Not Found`: Project not found

**Example Response:**
```json
[
  {
    "Id": 1,
    "Name": "Backend Development",
    "ProjectId": 1,
    "CreateDate": "2023-12-15T18:46:00"
  },
  {
    "Id": 2,
    "Name": "Frontend Development",
    "ProjectId": 1,
    "CreateDate": "2023-12-15T18:47:00"
  }
]
```

### 2. Get Single Task Group

**Endpoint:** `GET /api/groups/{group_id}`

**Description:** Retrieves a single task group by its ID.

**Authentication:** Required (user must have access to the project that owns the group)

**Parameters:**
- `group_id` (path parameter): The ID of the task group

**Response:**
- `200 OK`: Task group object
- `403 Forbidden`: User doesn't have access to the project
- `404 Not Found`: Task group not found

**Example Response:**
```json
{
  "Id": 1,
  "Name": "Backend Development",
  "ProjectId": 1,
  "CreateDate": "2023-12-15T18:46:00"
}
```

### 3. Create New Task Group

**Endpoint:** `POST /api/projects/{project_id}/groups`

**Description:** Creates a new task group within a project.

**Authentication:** Required (user must have access to the project)

**Parameters:**
- `project_id` (path parameter): The ID of the project

**Request Body:**
```json
{
  "Name": "New Task Group"
}
```

**Response:**
- `201 Created`: Created task group object
- `400 Bad Request`: Project ID mismatch or invalid data
- `403 Forbidden`: User doesn't have access to the project
- `404 Not Found`: Project not found

**Example Response:**
```json
{
  "Id": 3,
  "Name": "New Task Group",
  "ProjectId": 1,
  "CreateDate": "2023-12-15T18:48:00"
}
```

### 4. Update Task Group

**Endpoint:** `PUT /api/groups/{group_id}`

**Description:** Updates the name of an existing task group.

**Authentication:** Required (user must have access to the project that owns the group)

**Parameters:**
- `group_id` (path parameter): The ID of the task group
- `name` (query parameter): The new name for the task group

**Response:**
- `200 OK`: Updated task group object
- `403 Forbidden`: User doesn't have access to the project
- `404 Not Found`: Task group not found

**Example Response:**
```json
{
  "Id": 1,
  "Name": "Updated Task Group Name",
  "ProjectId": 1,
  "CreateDate": "2023-12-15T18:46:00"
}
```

### 5. Delete Task Group

**Endpoint:** `DELETE /api/groups/{group_id}`

**Description:** Deletes a task group and all its associated tasks (cascade delete).

**Authentication:** Required (user must have access to the project that owns the group)

**Parameters:**
- `group_id` (path parameter): The ID of the task group

**Response:**
- `200 OK`: Success message
- `403 Forbidden`: User doesn't have access to the project
- `404 Not Found`: Task group not found

**Example Response:**
```json
{
  "message": "Task group deleted successfully"
}
```

## Data Models

### TaskGroup

```json
{
  "Id": "integer",
  "Name": "string",
  "ProjectId": "integer",
  "CreateDate": "datetime"
}
```

### TaskGroupCreate

```json
{
  "Name": "string",
  "ProjectId": "integer"
}
```

## Authentication

All endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <your_token>
```

## Error Handling

The API returns standard HTTP status codes:
- `200 OK`: Success
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: User doesn't have permission
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Implementation Details

### Files Created/Modified:

1. **Created:** `backend/app/api/endpoints/task_groups.py` - API endpoints for task groups
2. **Modified:** `backend/app/main.py` - Added task groups router to the main application

### Key Features:

- **Project Association:** Each task group is associated with exactly one project
- **Access Control:** All operations check if the user has access to the project
- **Cascade Delete:** When a task group is deleted, all its tasks are also deleted
- **Consistent API Design:** Follows the same patterns as other endpoints in the application
- **Proper Error Handling:** Comprehensive error handling with appropriate HTTP status codes

### Security:

- All endpoints require authentication
- Users can only access task groups in projects they have access to
- Input validation is performed on all endpoints
- Proper error messages without exposing sensitive information

## Usage Examples

### Creating a Task Group

```bash
curl -X POST "http://localhost:8000/api/projects/1/groups" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"Name": "Backend Tasks"}'
```

### Getting All Task Groups for a Project

```bash
curl -X GET "http://localhost:8000/api/projects/1/groups" \
  -H "Authorization: Bearer your_token"
```

### Updating a Task Group

```bash
curl -X PUT "http://localhost:8000/api/groups/1?name=Updated%20Name" \
  -H "Authorization: Bearer your_token"
```

### Deleting a Task Group

```bash
curl -X DELETE "http://localhost:8000/api/groups/1" \
  -H "Authorization: Bearer your_token"