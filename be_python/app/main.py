import logging
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import sys
from pathlib import Path

# Thêm thư mục gốc vào sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from be_python.app.api.router import router
from be_python.app.utils.audio_utils import clean_temp_files
from be_python.app.config import TEMP_DIR

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger("app")

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Audio Search API",
    description="API trích xuất đặc trưng và tìm kiếm file audio tương tự",
    version="1.0.0"
)

# Thêm CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Có thể thay đổi thành các domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thêm router
app.include_router(router, prefix="/api")


# Xử lý lỗi toàn cục
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )


@app.get("/")
async def root():
    """
    Root endpoint cung cấp thông tin về API
    """
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


@app.on_event("startup")
async def startup_event():
    """
    Thực hiện các tác vụ khi khởi động server
    """
    logger.info("Khởi động ứng dụng Audio Search API")

    # Tạo thư mục temp nếu chưa có
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Dọn dẹp các file tạm thời cũ
    clean_temp_files()


@app.on_event("shutdown")
async def shutdown_event():
    """
    Thực hiện các tác vụ khi đóng server
    """
    logger.info("Đóng ứng dụng Audio Search API")

    # Dọn dẹp các file tạm thời
    clean_temp_files(older_than_hours=0)


if __name__ == "__main__":
    # Khởi chạy ứng dụng với uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)