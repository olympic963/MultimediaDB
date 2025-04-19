import os
import logging
import tempfile
from pathlib import Path
from typing import BinaryIO, Generator, Optional

import soundfile as sf
import numpy as np
from fastapi import UploadFile

from be_python.app.config import TEMP_DIR, SAMPLE_RATE, CHUNK_SIZE

logger = logging.getLogger(__name__)


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


def clean_temp_files(older_than_hours: int = 1):
    """
    Xóa các file tạm thời cũ hơn một khoảng thời gian nhất định

    Args:
        older_than_hours: Số giờ, file cũ hơn số giờ này sẽ bị xóa
    """
    import time
    current_time = time.time()

    for file in TEMP_DIR.glob("*"):
        if file.is_file():
            file_age = current_time - file.stat().st_mtime
            if file_age > older_than_hours * 3600:  # Convert hours to seconds
                try:
                    os.remove(file)
                    logger.info(f"Đã xóa file tạm thời: {file}")
                except Exception as e:
                    logger.error(f"Không thể xóa file tạm thời {file}: {str(e)}")


def get_audio_filename(file_path: str) -> str:
    """
    Lấy tên file từ đường dẫn đầy đủ

    Args:
        file_path: Đường dẫn đến file

    Returns:
        Tên file
    """
    return os.path.basename(file_path)