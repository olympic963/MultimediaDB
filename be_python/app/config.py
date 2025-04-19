import os
from pathlib import Path
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# Đường dẫn cơ sở
BASE_DIR = Path(__file__).resolve().parent.parent

# Thông tin cho Qdrant
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "audio_vectors")

# Đường dẫn đến thư mục audio
AUDIO_DATASET_PATH = os.getenv("AUDIO_DATASET_PATH", r"/Dataset/Bassoon")

# Tham số trích xuất đặc trưng
SAMPLE_RATE = 22050
N_MFCC = 40
HOP_LENGTH = 512
N_FFT = 2048

# Số lượng kết quả trả về
TOP_K = 3

# Thư mục tạm để lưu file upload
TEMP_DIR = BASE_DIR / "data" / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Kích thước chunk cho việc streaming (bytes)
CHUNK_SIZE = 1024 * 8  # 8KB