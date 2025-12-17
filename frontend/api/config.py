"""API Configuration"""

# Base API configuration
API_BASE_URL = "http://localhost:8000"

# API Endpoints
AUTH_ENDPOINTS = {
    "register": "/api/auth/register",
    "confirm_otp": "/api/auth/confirm-otp",
    "resend_otp": "/api/auth/again-otp",
    "login": "/api/auth/login",
    "fetch_user": "/api/auth/fetch"
}

USER_ENDPOINTS = {
    "get_users": "/api/users/",
    "get_user": "/api/users/{user_id}",
    "update_user": "/api/users/{user_id}",
    "delete_user": "/api/users/{user_id}"
}

PROJECT_ENDPOINTS = {
    "get_my_projects": "/api/projects/my",
    "get_all_projects": "/api/projects/",
    "get_project": "/api/projects/{project_id}",
    "create_project": "/api/projects/",
    "update_project": "/api/projects/{project_id}",
    "get_members": "/api/projects/{project_id}/members",
    "add_member": "/api/projects/{project_id}/members",
    "update_member": "/api/projects/{project_id}/members/{member_id}",
    "remove_member": "/api/projects/{project_id}/members/{member_id}"
}

TASK_GROUP_ENDPOINTS = {
    "get_groups": "/api/task_groups/projects/{project_id}/groups",
    "get_group": "/api/task_groups/groups/{group_id}",
    "create_group": "/api/task_groups/projects/{project_id}/groups",
    "update_group": "/api/task_groups/groups/{group_id}",
    "delete_group": "/api/task_groups/groups/{group_id}"
}

TASK_ENDPOINTS = {
    "get_tasks": "/api/tasks/projects/{project_id}/tasks",
    "create_task": "/api/tasks/projects/{project_id}/tasks"
}

FILE_ENDPOINTS = {
    "upload_file": "/api/files/projects/{project_id}/files",
    "get_files": "/api/files/projects/{project_id}/files"
}