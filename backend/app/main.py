from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.database import engine, Base
from app.api.endpoints import auth, users, projects, tasks, task_groups

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
app.include_router(task_groups.router, prefix="/task_groups/api", tags=["task_groups"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Workbench Flow API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}