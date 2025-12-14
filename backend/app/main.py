from fastapi import FastAPI
from app.database import engine, Base
from app.api.endpoints import items

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="My FastAPI Project",
    description="API с FastAPI и SQLAlchemy",
    version="1.0.0"
)

# Подключаем роутеры
app.include_router(items.router, prefix="/api", tags=["api"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI with SQLAlchemy"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}