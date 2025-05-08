import logging
import os
import sys
import asyncio
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api.router import router
from app.utils.audio_utils import clean_temp_files
from app.config import TEMP_DIR, TEMP_FILE_TTL_MINUTES

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("app")
logger.info("Đang khởi tạo file main.py")

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
            "reload": "/api/search/result/{query_id}",
            "stream": "/api/stream/{file_path}",
            "metadata": "/api/metadata/{file_path}",
        }
    }

async def periodic_clean_temp_files():
    while True:
        try:
            clean_temp_files()
            await asyncio.sleep(TEMP_FILE_TTL_MINUTES*60)  # Giảm để kiểm tra
        except Exception as e:
            logger.error(f"Lỗi khi chạy tác vụ định kỳ xóa file tạm: {str(e)}")
            await asyncio.sleep(10)

# Biến toàn cục để lưu task
background_task = None

@app.on_event("startup")
async def startup_event():
    try:
        os.makedirs(TEMP_DIR, exist_ok=True)
        if not os.access(TEMP_DIR, os.W_OK):
            logger.error(f"Không có quyền ghi vào {TEMP_DIR}")
            raise RuntimeError(f"Không có quyền ghi vào {TEMP_DIR}")
        logger.info(f"TEMP_DIR: {TEMP_DIR}")
        clean_temp_files()
        global background_task
        background_task = asyncio.create_task(periodic_clean_temp_files())
    except Exception as e:
        logger.error(f"Lỗi trong startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    try:
        global background_task
        if background_task:
            background_task.cancel()
        clean_temp_files()
    except Exception as e:
        logger.error(f"Lỗi trong shutdown: {str(e)}")
        raise

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")