from fastapi import FastAPI
from app.application.routes import router

app = FastAPI(title='ProjectManagement API', version='1.0.0')

app.include_router(router)