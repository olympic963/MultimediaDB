import asyncio
import logging
import os
import tempfile
import time
from typing import Generator

import soundfile as sf
from fastapi import UploadFile

from app.config import TEMP_DIR, CHUNK_SIZE,TEMP_FILE_TTL_MINUTES

logger = logging.getLogger(__name__)
# Tập hợp để theo dõi các file đang được stream
active_streams = set()
# Khóa để đảm bảo tính đồng bộ khi truy cập active_streams
active_streams_lock = asyncio.Lock()

async def save_upload_file(upload_file: UploadFile) -> str:
    """
    Lưu file upload vào thư mục tạm

    Args:
        upload_file: File được upload

    Returns:
        Đường dẫn đến file đã lưu
    """
    try:
        # Tạo tên file tạm thời
        file_extension = os.path.splitext(upload_file.filename)[1]
        temp_file = TEMP_DIR / f"{next(tempfile._get_candidate_names())}{file_extension}"

        # Lưu nội dung file
        with open(temp_file, "wb") as f:
            content = await upload_file.read()
            f.write(content)

        logger.info(f"Đã lưu file upload tạm thời: {temp_file}")
        return str(temp_file)
    except Exception as e:
        logger.error(f"Lỗi khi lưu file upload: {str(e)}")
        raise


def file_iterator(file_path: str, chunk_size: int = CHUNK_SIZE) -> Generator[bytes, None, None]:
    """
    Tạo iterator để đọc file theo chunks

    Args:
        file_path: Đường dẫn đến file
        chunk_size: Kích thước của mỗi chunk

    Returns:
        Generator cho các chunks của file
    """
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


def get_audio_metadata(file_path: str) -> dict:
    """
    Lấy metadata của file audio

    Args:
        file_path: Đường dẫn đến file audio

    Returns:
        Dict chứa metadata
    """
    try:
        info = sf.info(file_path)
        return {
            "duration": info.duration,
            "channels": info.channels,
            "sample_rate": info.samplerate,
            "format": info.format,
            "subtype": info.subtype
        }
    except Exception as e:
        logger.error(f"Không thể đọc metadata của file audio {file_path}: {str(e)}")
        return {
            "error": str(e)
        }

def clean_temp_files(older_than_minutes: float = TEMP_FILE_TTL_MINUTES, max_retries: int = 3, retry_delay: float = 1.0):
    """
    Xóa các file tạm thời cũ hơn một khoảng thời gian nhất định
    Args:
        older_than_minutes: Số phút, file cũ hơn sẽ bị xóa
        max_retries: Số lần thử lại nếu xóa thất bại
        retry_delay: Thời gian chờ giữa các lần thử (giây)
    """
    current_time = time.time()
    for file in TEMP_DIR.glob("*"):
        if file.is_file():
            file_age = current_time - file.stat().st_mtime
            file_path = str(file)
            # Chỉ xóa nếu file không đang được stream và đủ tuổi
            if file_age > older_than_minutes * 60 and file_path not in active_streams:
                for attempt in range(max_retries):
                    try:
                        os.remove(file)
                        logger.info(f"Đã xóa file tạm thời: {file}")
                        break
                    except OSError as e:
                        if attempt < max_retries - 1:
                            logger.warning(f"Thử lại xóa file {file} (lần {attempt + 1}): {str(e)}")
                            time.sleep(retry_delay)
                        else:
                            logger.error(f"Không thể xóa file tạm thời {file} sau {max_retries} lần thử: {str(e)}")

def get_audio_filename(file_path: str) -> str:
    """
    Lấy tên file từ đường dẫn đầy đủ

    Args:
        file_path: Đường dẫn đến file

    Returns:
        Tên file
    """
    return os.path.basename(file_path)


def create_temp_file_url(file_path: str, base_url: str = None) -> str:
    """
    Tạo URL tạm thời cho file tạm đã lưu
    Args:
        file_path: Đường dẫn đến file tạm đã lưu
        base_url: URL cơ sở của API, nếu None sẽ chỉ trả về đường dẫn tương đối
    Returns:
        URL tạm thời để truy cập file
    """
    # Lấy tên file từ đường dẫn đầy đủ
    file_name = os.path.basename(file_path)

    # Tạo URL tương đối
    relative_url = f"/api/stream/{file_name}"

    # Nếu có base_url, trả về URL đầy đủ
    if base_url:
        return f"{base_url.rstrip('/')}{relative_url}"

    # Ngược lại trả về URL tương đối
    return relative_url