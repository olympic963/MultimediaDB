import logging
import os
import time

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from be_python.app.api.models import SearchResponse, AudioSearchResult, ErrorResponse, RequestType
from be_python.app.database.qdrant_manager import QdrantManager
from be_python.app.feature_extractor import AudioFeatureExtractor
from be_python.app.utils.audio_utils import save_upload_file, file_iterator, create_temp_file_url

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
        request: Request = None,
        feature_extractor: AudioFeatureExtractor = Depends(get_feature_extractor),
        qdrant_manager: QdrantManager = Depends(get_qdrant_manager)
):
    """ Tìm kiếm các file audio tương tự với file được upload """
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

        # Tạo URL tạm thời cho file truy vấn
        base_url = str(request.base_url) if request else None
        query_file_url = create_temp_file_url(temp_file_path, base_url)

        # Đo thời gian trích xuất đặc trưng
        start_extraction_time = time.time()
        features = feature_extractor.extract_features(temp_file_path)
        query_vector = features["vector"]
        extraction_time = time.time() - start_extraction_time
        logger.info(f"Thời gian trích xuất đặc trưng: {extraction_time:.4f} giây")

        # Đo thời gian truy vấn Qdrant
        start_query_time = time.time()
        search_results = qdrant_manager.search_similar(query_vector)
        query_time = time.time() - start_query_time
        logger.info(f"Thời gian truy vấn Qdrant: {query_time:.4f} giây")

        # Chuẩn bị kết quả trả về theo template SearchResponse
        results = [
            AudioSearchResult(
                file_name=item["file_name"],
                file_type=item["file_type"],
                file_size_kb=item["file_size_kb"],
                sample_rate=item["sample_rate"],
                channel=item["channel"],
                samples=item["samples"],
                duration=item["duration"],
                subtype=item["subtype"],
                similarity=item["similarity"]
            )
            for item in search_results
        ]

        # Trả về theo template SearchResponse với URL của file truy vấn và thời gian xử lý
        return SearchResponse(
            request_type=RequestType.file,
            query_file=file.filename,
            query_string="",
            query_file_url=query_file_url,
            results=results,
            extraction_time=extraction_time,  # Thêm thời gian trích xuất đặc trưng
        )
    except Exception as e:
        logger.error(f"Lỗi khi xử lý tìm kiếm: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý tìm kiếm: {str(e)}"
        )


@router.get(
    "/metadata",
    response_model=SearchResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_audio_file_metadata(
        query_string: str,
        qdrant_manager: QdrantManager = Depends(get_qdrant_manager)
):
    """ Lấy metadata của các file audio có file_name chứa query_string, trả về theo template SearchResponse """
    try:
        # Tìm kiếm các file có file_name chứa query_string
        search_results = qdrant_manager.search_by_filename(query_string)
        if not search_results:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy file nào có tên chứa: {query_string}"
            )
        # Chuẩn bị kết quả trả về
        results = [
            AudioSearchResult(
                file_name=item["file_name"],
                file_type=item["file_type"],
                file_size_kb=item["file_size_kb"],
                sample_rate=item["sample_rate"],
                channel=item["channel"],
                samples=item["samples"],
                duration=item["duration"],
                subtype=item["subtype"],
                similarity=item["similarity"]
            )
            for item in search_results
        ]
        # Trả về theo template SearchResponse
        return SearchResponse(
            request_type=RequestType.metadata,
            query_file=None,
            query_string=query_string,
            query_file_url=None,  # Không có URL tạm thời
            results=results
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi khi lấy metadata: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy metadata: {str(e)}"
        )


@router.get(
    "/stream/{file_name}",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def stream_audio(
        file_name: str,
        request: Request
):
    """ Stream file audio từ thư mục tạm """
    try:
        # Xây dựng đường dẫn đầy đủ đến file trong thư mục tạm
        from be_python.app.config import TEMP_DIR
        file_path = os.path.join(TEMP_DIR, file_name)

        # Kiểm tra file tồn tại
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"File không tồn tại: {file_name}"
            )

        # Phần còn lại của hàm giữ nguyên
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
