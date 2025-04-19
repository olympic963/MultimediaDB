from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AudioSearchResult(BaseModel):
    """Model cho kết quả tìm kiếm audio"""
    file_path: str = Field(..., description="Đường dẫn đến file audio")
    similarity: float = Field(..., description="Điểm số tương đồng")
    filename: str = Field(..., description="Tên file audio")

class SearchResponse(BaseModel):
    """Model cho response API tìm kiếm"""
    query_file: str = Field(..., description="Tên file query")
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