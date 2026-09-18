from fastapi import FastAPI
from app import config, database
from app.routers import auth

app = FastAPI()

app.include_router(auth.router)