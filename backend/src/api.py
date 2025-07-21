from fastapi import FastAPI
from .auth.controller import router as auth_router
from .candidates.controller import router as candidates_router

def register_routes(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(candidates_router)