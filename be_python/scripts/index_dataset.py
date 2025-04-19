#!/usr/bin/env python3
import sys
import os
import logging
import time
from pathlib import Path

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
        logging.FileHandler("indexing.log", encoding='utf-8')
    ]
)

logger = logging.getLogger("indexing")

def index_audio_dataset():
    """
    Trích xuất đặc trưng từ tất cả các file audio trong dataset và lưu vào database
    Collection sẽ được xóa và tạo lại.
    """
    start_time = time.time()

    logger.info(f"Bắt đầu quá trình trích xuất đặc trưng từ {AUDIO_DATASET_PATH}")

    try:
        # Khởi tạo các thành phần
        feature_extractor = AudioFeatureExtractor()
        qdrant_manager = QdrantManager()

        # Kiểm tra thư mục dataset
        if not os.path.exists(AUDIO_DATASET_PATH):
            logger.error(f"Thư mục dataset không tồn tại: {AUDIO_DATASET_PATH}")
            return

        # Trích xuất đặc trưng từ các file audio
        logger.info("Đang trích xuất đặc trưng và metadata từ files audio...")
        feature_dict = feature_extractor.process_audio_directory(AUDIO_DATASET_PATH)

        if not feature_dict:
            logger.warning("Không tìm thấy file audio nào trong thư mục dataset")
            return

        # Lưu vào database, xóa và tạo lại collection
        logger.info(f"Đang xóa collection cũ và lưu {len(feature_dict)} vectors vào Qdrant database...")
        qdrant_manager.insert_vectors(feature_dict, recreate_collection=True)

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
        logger.info(f"Hoàn thành quá trình indexing trong {end_time - start_time:.2f} giây")
        logger.info(f"Số vectors trong database: {vectors_count}")

    except Exception as e:
        logger.error(f"Lỗi khi indexing dataset: {str(e)}")

if __name__ == "__main__":
    index_audio_dataset()