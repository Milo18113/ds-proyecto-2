from fastapi import FastAPI
from app.repositories.database import create_tables
from app.application.routes import router

app = FastAPI(title="Fintech Mini Bank API", version="1.0.0")

app.include_router(router)


@app.on_event("startup")
def on_startup():
    create_tables()