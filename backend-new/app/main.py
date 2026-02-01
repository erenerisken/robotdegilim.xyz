from fastapi import FastAPI

from app.api.routes import router
from app.core.logging import setup_logging

app = FastAPI()
app.include_router(router)
setup_logging()
