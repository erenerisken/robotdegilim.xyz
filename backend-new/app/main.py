from fastapi import FastAPI

from app.api.routes import router
from app.core.logging import setup_logging

app = FastAPI()
setup_logging()
app.include_router(router)
