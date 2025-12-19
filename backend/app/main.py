from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.database import engine, Base
from app.api.endpoints import (
    auth,
    users,
    projects,
    tasks,
    task_groups,
    store_files,
    project_roles,
    marks,
)

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Workbench Flow API",
    description="API для управления проектами и задачами",
    version="1.0.0"
)

security = HTTPBearer()

# Подключаем роутеры
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(task_groups.router, prefix="/api/task_groups", tags=["task_groups"])
app.include_router(store_files.router, prefix="/api/files", tags=["store_files"])
app.include_router(project_roles.router, prefix="/api", tags=["project_roles"])
app.include_router(marks.router, prefix="/api", tags=["marks"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Workbench Flow API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}