from typing import Union
from local_logger import configure_logging, LogLevels
import logging

from fastapi import FastAPI

configure_logging(LogLevels.info)

app = FastAPI()


@app.get("/")
def read_root() ->  dict:
    logging.info(f"Root endpoint accessed")
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None) -> dict:
    return {"item_id": item_id, "q": q}