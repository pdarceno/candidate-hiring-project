from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import register_routes
from .local_logger import configure_logging, LogLevels

configure_logging(LogLevels.info)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_routes(app)