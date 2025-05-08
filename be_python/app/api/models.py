from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class RequestType(str, Enum):
    metadata = "metadata"
    file = "file"

class AudioSearchResult(BaseModel):
    """Model cho kết quả tìm kiếm audio"""
    file_name: str = Field(..., description="Tên file audio")
    file_type: str = Field(..., description="Loại file audio (ví dụ: wav, mp3)")
    file_size_kb: float = Field(..., description="Kích thước file (KB)")
    sample_rate: int = Field(..., description="Tần số mẫu (Hz)")
    channel: int = Field(..., description="Số kênh âm thanh (mono/stereo)")
    samples: int = Field(..., description="Tổng số mẫu âm thanh")
    duration: float = Field(..., description="Thời lượng file (giây)")
    subtype: str = Field(..., description="Định dạng phụ (ví dụ: PCM_16)")
    similarity: float = Field(..., description="Điểm số tương đồng")

class SearchResponse(BaseModel):
    """Model cho response API tìm kiếm"""
    query_id: str = Field(..., description="ID duy nhất của yêu cầu tìm kiếm")
    request_type: RequestType = Field(..., description="Loại yêu cầu: metadata hoặc file")
    query_string: str = Field(..., description="Chuỗi query")
    temp_file_name: Optional[str] = Field(None, description="Tên file tạm của file truy vấn")
    results: List[AudioSearchResult] = Field(..., description="Danh sách kết quả tìm kiếm")

class DatabaseInfo(BaseModel):
    """Model cho thông tin về database"""
    collection_name: str = Field(..., description="Tên collection")
    vectors_count: Optional[int] = Field(None, description="Số lượng vectors")
    status: str = Field(..., description="Trạng thái collection")

class ErrorResponse(BaseModel):
    """Model cho response lỗi"""
    error: str = Field(..., description="Thông báo lỗi")
    detail: Optional[str] = Field(None, description="Chi tiết lỗi")
