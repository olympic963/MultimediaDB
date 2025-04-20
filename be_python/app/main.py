import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from be_python.app.api.router import router
from be_python.app.utils.audio_utils import clean_temp_files
from be_python.app.config import TEMP_DIR

# Cấu hình logging với encoding utf-8
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("app")

app = FastAPI(
    title="Audio Search API",
    description="API trích xuất đặc trưng và tìm kiếm file audio tương tự",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )


@app.get("/")
async def root():
    return {
        "message": "Audio Search API",
        "version": "1.0.0",
        "docs": "/docs",
        "api_endpoints": {
            "search": "/api/search",
            "stream": "/api/stream/{file_path}",
            "metadata": "/api/metadata/{file_path}",
            "db_info": "/api/db-info"
        }
    }


@asynccontextmanager
async def lifespan():
    logger.info("Khoi dong ung dung Audio Search API")
    os.makedirs(TEMP_DIR, exist_ok=True)
    clean_temp_files()
    yield
    logger.info("Dong ung dung Audio Search API")
    clean_temp_files(older_than_hours=0)


app.lifespan_context = lifespan

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
