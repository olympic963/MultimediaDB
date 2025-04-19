import os
from typing import List, Dict, Any
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from be_python.app.feature_extractor import AudioFeatureExtractor
from be_python.app.database.qdrant_manager import QdrantManager
from be_python.app.utils.audio_utils import save_upload_file, file_iterator, get_audio_metadata, get_audio_filename
from be_python.app.api.models import SearchResponse, AudioSearchResult, DatabaseInfo, ErrorResponse

router = APIRouter()
logger = logging.getLogger(__name__)


# Dependency để lấy các instances cần thiết
def get_feature_extractor():
    return AudioFeatureExtractor()


def get_qdrant_manager():
    return QdrantManager()


@router.post(
    "/search",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def search_similar_audio(
        file: UploadFile = File(...),
        feature_extractor: AudioFeatureExtractor = Depends(get_feature_extractor),
        qdrant_manager: QdrantManager = Depends(get_qdrant_manager)
):
    """
    Tìm kiếm các file audio tương tự với file được upload
    """
    try:
        # Kiểm tra file extension hợp lệ
        valid_extensions = ['.wav', '.mp3', '.flac', '.ogg']
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in valid_extensions:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Định dạng file không hỗ trợ. Các định dạng hỗ trợ: {', '.join(valid_extensions)}"
            )

        # Lưu file upload vào thư mục tạm
        temp_file_path = await save_upload_file(file)

        # Trích xuất đặc trưng từ file audio
        query_vector = feature_extractor.extract_features(temp_file_path)

        # Tìm kiếm các file tương tự
        search_results = qdrant_manager.search_similar(query_vector)

        # Chuẩn bị kết quả trả về
        results = []
        for item in search_results:
            file_path = item["file_path"]
            results.append(AudioSearchResult(
                file_path=file_path,
                similarity=item["similarity"],
                filename=get_audio_filename(file_path)
            ))

        # Trả về kết quả
        return SearchResponse(
            query_file=file.filename,
            results=results
        )
    except Exception as e:
        logger.error(f"Lỗi khi xử lý tìm kiếm: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý tìm kiếm: {str(e)}"
        )


@router.get(
    "/stream/{file_path:path}",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def stream_audio(
        file_path: str,
        request: Request
):
    """
    Stream file audio
    """
    try:
        # Kiểm tra file tồn tại
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"File không tồn tại: {file_path}"
            )

        # Lấy thông tin file
        file_size = os.path.getsize(file_path)

        # Xác định content_type dựa trên phần mở rộng
        file_ext = os.path.splitext(file_path)[1].lower()
        content_type_map = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.flac': 'audio/flac',
            '.ogg': 'audio/ogg',
        }
        content_type = content_type_map.get(file_ext, 'application/octet-stream')

        # Tạo iterator để streaming file
        file_stream = file_iterator(file_path)

        # Trả về response streaming
        response = StreamingResponse(
            file_stream,
            media_type=content_type
        )

        # Thêm các headers cần thiết
        response.headers["Content-Disposition"] = f"inline; filename={os.path.basename(file_path)}"
        response.headers["Accept-Ranges"] = "bytes"
        response.headers["Content-Length"] = str(file_size)

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi streaming file audio: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi streaming file audio: {str(e)}"
        )


@router.get(
    "/metadata/{file_path:path}",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_audio_file_metadata(
        file_path: str
):
    """
    Lấy metadata của file audio
    """
    try:
        # Kiểm tra file tồn tại
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"File không tồn tại: {file_path}"
            )

        # Lấy metadata
        metadata = get_audio_metadata(file_path)

        # Thêm thông tin file vào metadata
        metadata["filename"] = os.path.basename(file_path)
        metadata["file_size"] = os.path.getsize(file_path)

        return metadata
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi lấy metadata của file audio: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy metadata của file audio: {str(e)}"
        )


@router.get("/db-info", response_model=DatabaseInfo)
async def get_database_info(
        qdrant_manager: QdrantManager = Depends(get_qdrant_manager)
):
    """
    Lấy thông tin về Qdrant vector database
    """
    try:
        db_info = qdrant_manager.get_collection_info()
        return DatabaseInfo(
            collection_name=db_info.get("name"),
            vectors_count=db_info.get("vectors_count"),
            status=db_info.get("status")
        )
    except Exception as e:
        logger.error(f"Lỗi khi lấy thông tin database: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy thông tin database: {str(e)}"
        )