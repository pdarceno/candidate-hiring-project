from fastapi import FastAPI
from .auth.controller import router as auth_router
from .candidates.controller import router as candidates_router
from .applications.controller import router as applications_router

def register_routes(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(candidates_router)
    app.include_router(applications_router) 