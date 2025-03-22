from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
import os

from app.api.main import api_router
from app.api.routes.websocket import router as websocket_router
from app.core.config import settings
from app.core.db import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="REAL TIME CHAT APPLICATION",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


# Set all CORS enabled origins
app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
async def root():
    return {"message": "REAL TIME CHAT APPLICATION: v0.0.1"}


app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(websocket_router)

# Mount static files directory
static_files_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "")
app.mount("/static", StaticFiles(directory=static_files_dir), name="static")
