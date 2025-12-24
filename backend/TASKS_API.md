# Tasks API Documentation

This document describes the comprehensive Tasks API that has been implemented for managing tasks within projects.

## Overview

The Tasks API provides endpoints for creating, reading, updating, and deleting tasks. Tasks are associated with projects through task groups and support various features like assignment, status tracking, deadlines, and more.

## Base URL

All endpoints are available under the `/api/tasks` prefix.

## Endpoints

### 1. Get Single Task

**Endpoint:** `GET /api/tasks/{task_id}`

**Description:** Retrieves a single task by its ID with full details.

**Authentication:** Required

**Parameters:**
- `task_id` (path parameter): The ID of the task

**Response:**
- `200 OK`: Task object with details
- `403 Forbidden`: User doesn't have access to the project
- `404 Not Found`: Task not found

**Example Response:**
```json
{
  "Id": 1,
  "Title": "Implement authentication",
  "Text": "Implement JWT authentication for the API",
  "AuthorId": 1,
  "TargetId": 2,
  "StateId": 1,
  "GroupId": 1,
  "CreateDate": "2023-12-16T11:35:00",
  "IsClosed": false,
  "DeadLine": "2023-12-20",
  "author": {
    "Id": 1,
    "Username": "john_doe",
    "Email": "john@example.com",
    "CreateDate": "2023-12-15T10:00:00",
    "IsDeleted": false
  },
  "target": {
    "Id": 2,
    "Username": "jane_doe",
    "Email": "jane@example.com",
    "CreateDate": "2023-12-15T11:00:00",
    "IsDeleted": false
  },
  "state": {
    "Id": 1,
    "Name": "In Progress"
  },
  "group": {
    "Id": 1,
    "Name": "Backend Development",
    "ProjectId": 1
  },
  "comments": [],
  "task_files": [],
  "pins": []
}
```

### 2. Get All Tasks

**Endpoint:** `GET /api/tasks/`

**Description:** Retrieves all tasks (accessible to all authenticated users).

**Authentication:** Required

**Parameters:**
- `skip` (query parameter, optional): Number of tasks to skip (default: 0)
- `limit` (query parameter, optional): Maximum number of tasks to return (default: 100)

**Response:**
- `200 OK`: Array of task objects

**Example Response:**
```json
[
  {
    "Id": 1,
    "Title": "Implement authentication",
    "Text": "Implement JWT authentication for the API",
    "AuthorId": 1,
    "TargetId": 2,
    "StateId": 1,
    "GroupId": 1,
    "CreateDate": "2023-12-16T11:35:00",
    "IsClosed": false,
    "DeadLine": "2023-12-20"
  },
  {
    "Id": 2,
    "Title": "Design database schema",
    "Text": "Design the database schema for the project",
    "AuthorId": 1,
    "TargetId": 3,
    "StateId": 0,
    "GroupId": 1,
    "CreateDate": "2023-12-16T11:40:00",
    "IsClosed": false,
    "DeadLine": "2023-12-18"
  }
]
```

### 3. Get My Tasks

**Endpoint:** `GET /api/tasks/my`

**Description:** Retrieves tasks assigned to or created by the current user.

**Authentication:** Required

**Parameters:**
- `closed` (query parameter, optional): Filter by task status (true/false)

**Response:**
- `200 OK`: Array of task objects with details

**Example Request:**
```bash
# Get only open tasks
curl -X GET "http://localhost:8000/api/tasks/my?closed=false" \
  -H "Authorization: Bearer your_token"

# Get only closed tasks
curl -X GET "http://localhost:8000/api/tasks/my?closed=true" \
  -H "Authorization: Bearer your_token"

# Get all tasks (both open and closed)
curl -X GET "http://localhost:8000/api/tasks/my" \
  -H "Authorization: Bearer your_token"
```

### 4. Get Project Tasks

**Endpoint:** `GET /api/projects/{project_id}/tasks`

**Description:** Retrieves all tasks for a specific project.

**Authentication:** Required (user must have access to the project)

**Parameters:**
- `project_id` (path parameter): The ID of the project
- `closed` (query parameter, optional): Filter by task status (true/false)

**Response:**
- `200 OK`: Array of task objects with details
- `403 Forbidden`: User doesn't have access to the project
- `404 Not Found`: Project not found

### 5. Create New Task

**Endpoint:** `POST /api/projects/{project_id}/tasks`

**Description:** Creates a new task in a project.

**Authentication:** Required (user must have access to the project)

**Parameters:**
- `project_id` (path parameter): The ID of the project

**Request Body:**
```json
{
  "Title": "Implement user registration",
  "Text": "Implement user registration endpoint with email verification",
  "TargetId": 2,
  "StateId": 0,
  "GroupId": 1,
  "DeadLine": "2023-12-25"
}
```

**Response:**
- `201 Created`: Created task object
- `400 Bad Request`: Invalid data or validation errors
- `403 Forbidden`: User doesn't have access to the project
- `404 Not Found`: Project, target user, or task group not found

**Example Response:**
```json
{
  "Id": 3,
  "Title": "Implement user registration",
  "Text": "Implement user registration endpoint with email verification",
  "AuthorId": 1,
  "TargetId": 2,
  "StateId": 0,
  "GroupId": 1,
  "CreateDate": "2023-12-16T11:45:00",
  "IsClosed": false,
  "DeadLine": "2023-12-25"
}
```

### 6. Update Task

**Endpoint:** `PUT /api/tasks/{task_id}`

**Description:** Updates an existing task.

**Authentication:** Required (user must have access to the project)

**Parameters:**
- `task_id` (path parameter): The ID of the task

**Request Body:**
```json
{
  "Title": "Updated task title",
  "Text": "Updated task description",
  "TargetId": 3,
  "StateId": 1,
  "GroupId": 2,
  "IsClosed": false,
  "DeadLine": "2023-12-22"
}
```

**Response:**
- `200 OK`: Updated task object
- `400 Bad Request`: Invalid data or validation errors
- `403 Forbidden`: User doesn't have access to the project
- `404 Not Found`: Task, target user, or task group not found

### 7. Delete Task

**Endpoint:** `DELETE /api/tasks/{task_id}`

**Description:** Deletes a task.

**Authentication:** Required (user must have access to the project)

**Parameters:**
- `task_id` (path parameter): The ID of the task

**Response:**
- `200 OK`: Success message
- `403 Forbidden`: User doesn't have access to the project
- `404 Not Found`: Task not found

**Example Response:**
```json
{
  "message": "Task deleted successfully"
}
```

### 8. Close Task

**Endpoint:** `POST /api/tasks/{task_id}/close`

**Description:** Marks a task as closed/completed.

**Authentication:** Required (user must have access to the project)

**Parameters:**
- `task_id` (path parameter): The ID of the task

**Response:**
- `200 OK`: Success message and updated task
- `403 Forbidden`: User doesn't have access to the project
- `404 Not Found`: Task not found

**Example Response:**
```json
{
  "message": "Task closed successfully",
  "task": {
    "Id": 1,
    "Title": "Implement authentication",
    "Text": "Implement JWT authentication for the API",
    "AuthorId": 1,
    "TargetId": 2,
    "StateId": 1,
    "GroupId": 1,
    "CreateDate": "2023-12-16T11:35:00",
    "IsClosed": true,
    "DeadLine": "2023-12-20"
  }
}
```

### 9. Reopen Task

**Endpoint:** `POST /api/tasks/{task_id}/reopen`

**Description:** Reopens a closed task.

**Authentication:** Required (user must have access to the project)

**Parameters:**
- `task_id` (path parameter): The ID of the task

**Response:**
- `200 OK`: Success message and updated task
- `403 Forbidden`: User doesn't have access to the project
- `404 Not Found`: Task not found

**Example Response:**
```json
{
  "message": "Task reopened successfully",
  "task": {
    "Id": 1,
    "Title": "Implement authentication",
    "Text": "Implement JWT authentication for the API",
    "AuthorId": 1,
    "TargetId": 2,
    "StateId": 1,
    "GroupId": 1,
    "CreateDate": "2023-12-16T11:35:00",
    "IsClosed": false,
    "DeadLine": "2023-12-20"
  }
}
```

## Data Models

### Task

```json
{
  "Id": "integer",
  "Title": "string",
  "Text": "string",
  "AuthorId": "integer",
  "TargetId": "integer (optional)",
  "StateId": "integer",
  "GroupId": "integer (optional)",
  "CreateDate": "datetime",
  "IsClosed": "boolean",
  "DeadLine": "date (optional)"
}
```

### TaskCreate

```json
{
  "Title": "string",
  "Text": "string",
  "TargetId": "integer (optional)",
  "StateId": "integer (optional)",
  "GroupId": "integer (optional)",
  "DeadLine": "date (optional)"
}
```

### TaskUpdate

```json
{
  "Title": "string (optional)",
  "Text": "string (optional)",
  "TargetId": "integer (optional)",
  "StateId": "integer (optional)",
  "GroupId": "integer (optional)",
  "IsClosed": "boolean (optional)",
  "DeadLine": "date (optional)"
}
```

### TaskWithDetails

Includes all Task fields plus:
- `author`: User object
- `target`: User object (if assigned)
- `state`: TaskState object
- `group`: TaskGroup object (if in group)
- `comments`: Array of Comment objects
- `task_files`: Array of TaskFile objects
- `pins`: Array of Pin objects

## Key Features

### Access Control
- All task operations require proper project access
- Users can only access tasks in projects they belong to
- Comprehensive permission checking for all endpoints

### Task States
- Tasks can have different states (e.g., "To Do", "In Progress", "Done")
- State management through TaskState model

### Task Assignment
- Tasks can be assigned to specific users (TargetId)
- Assignment validation ensures target users exist

### Task Groups
- Tasks belong to task groups within projects
- Group validation ensures tasks stay within their project
- Prevents moving tasks between different projects

### Deadlines
- Optional deadline dates for tasks
- Date validation and proper formatting

### Task Lifecycle
- Create tasks with full details
- Update any task attribute
- Close/complete tasks
- Reopen closed tasks
- Delete tasks when no longer needed

### Relationships
- Tasks belong to users (author and target)
- Tasks belong to task groups
- Tasks have states
- Tasks can have comments
- Tasks can have attached files
- Tasks can be pinned by users

## Implementation Details

### Files Created/Modified:

1. **Modified:** `backend/app/api/endpoints/tasks.py` - Complete task API implementation
2. **Already Integrated:** `backend/app/main.py` - Task router already included

### Validation Rules:

- Task titles must be 75 characters or less
- Task text can be long-form (Text type)
- Target users must exist in the system
- Task groups must belong to the same project
- Tasks cannot be moved between different projects
- Deadline dates must be valid

### Error Handling:

- `400 Bad Request`: Invalid input data or validation errors
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: User doesn't have access to the project
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server errors

## Usage Examples

### Creating a Task

```bash
curl -X POST "http://localhost:8000/api/projects/1/tasks" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "Title": "Fix authentication bug",
    "Text": "Fix the issue with JWT token expiration",
    "TargetId": 2,
    "StateId": 1,
    "GroupId": 1,
    "DeadLine": "2023-12-18"
  }'
```

### Getting My Open Tasks

```bash
curl -X GET "http://localhost:8000/api/tasks/my?closed=false" \
  -H "Authorization: Bearer your_token"
```

### Updating a Task

```bash
curl -X PUT "http://localhost:8000/api/tasks/1" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "StateId": 2,
    "IsClosed": true
  }'
```

### Closing a Task

```bash
curl -X POST "http://localhost:8000/api/tasks/1/close" \
  -H "Authorization: Bearer your_token"
```

### Getting Project Tasks

```bash
curl -X GET "http://localhost:8000/api/projects/1/tasks" \
  -H "Authorization: Bearer your_token"
```

## Security Considerations

- All endpoints require JWT authentication
- Project access is verified for all operations
- Users can only access tasks in projects they belong to
- Input validation prevents invalid data
- Proper error messages without exposing sensitive information

The Tasks API provides a comprehensive solution for task management within projects, with robust access control, validation, and error handling.