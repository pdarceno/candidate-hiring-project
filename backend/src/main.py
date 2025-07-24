from fastapi import FastAPI
from .api import register_routes
from .local_logger import configure_logging, LogLevels

configure_logging(LogLevels.info)

app = FastAPI()

register_routes(app)