#!/usr/bin/env python3
import sys
import os
import logging
import time
from pathlib import Path
import argparse

# Đặt mã hóa stdout thành UTF-8 để tránh lỗi UnicodeEncodeError
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Thêm thư mục gốc vào sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from be_python.app.feature_extractor import AudioFeatureExtractor
from be_python.app.database.qdrant_manager import QdrantManager
from be_python.app.config import AUDIO_DATASET_PATH

# Cấu hình logging với mã hóa UTF-8
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("index_new_data.log", encoding='utf-8')
    ]
)

logger = logging.getLogger("index_new_data")

def index_new_audio_data(directory_path: str):
    """
    Trích xuất đặc trưng từ các file audio mới trong thư mục và chèn vào Qdrant database
    Collection hiện có sẽ được giữ nguyên, chỉ chèn các file mới.
    """
    start_time = time.time()

    logger.info(f"Bắt đầu quá trình trích xuất đặc trưng từ {directory_path}")

    try:
        # Khởi tạo các thành phần
        feature_extractor = AudioFeatureExtractor()
        qdrant_manager = QdrantManager()

        # Kiểm tra thư mục
        if not os.path.exists(directory_path):
            logger.error(f"Thư mục không tồn tại: {directory_path}")
            return

        # Trích xuất đặc trưng từ các file audio
        logger.info("Đang trích xuất đặc trưng và metadata từ files audio...")
        feature_dict = feature_extractor.process_audio_directory(directory_path)

        if not feature_dict:
            logger.warning("Không tìm thấy file audio nào trong thư mục")
            return

        # Chèn vào database, giữ nguyên collection
        logger.info(f"Đang kiểm tra và chèn {len(feature_dict)} vectors mới vào Qdrant database...")
        qdrant_manager.insert_vectors(feature_dict, recreate_collection=False)

        # Lấy thông tin database sau khi thêm dữ liệu
        try:
            db_info = qdrant_manager.get_collection_info()
            vectors_count = db_info.get('points_count', 'N/A')
            collection_name = db_info.get('name', 'N/A')
            logger.info(f"Collection: {collection_name}")
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin collection: {str(e)}")
            vectors_count = 'N/A'

        # Hiển thị kết quả
        end_time = time.time()
        logger.info(f"Hoàn thành quá trình chèn dữ liệu mới trong {end_time - start_time:.2f} giây")
        logger.info(f"Số vectors trong database: {vectors_count}")

    except Exception as e:
        logger.error(f"Lỗi khi chèn dữ liệu mới: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chèn dữ liệu audio mới vào Qdrant database")
    parser.add_argument(
        "--directory",
        type=str,
        default=AUDIO_DATASET_PATH,
        help="Đường dẫn đến thư mục chứa file audio mới"
    )
    args = parser.parse_args()

    index_new_audio_data(args.directory)