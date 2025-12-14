from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.database import engine, Base
from app.api.endpoints import auth, users, projects, tasks

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
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(projects.router, prefix="/api", tags=["projects"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Workbench Flow API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}