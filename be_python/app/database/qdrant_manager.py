import logging
import os
from typing import Dict, List, Any
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

from app.config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION_NAME, TOP_K

logger = logging.getLogger(__name__)


class QdrantManager:
    """
    Quản lý Qdrant vector database
    """

    def __init__(self):
        # Khởi tạo kết nối đến Qdrant server
        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self.collection_name = QDRANT_COLLECTION_NAME

    def create_collection(self, vector_size: int, recreate_collection: bool = False):
        """
        Tạo collection trong Qdrant, tùy chọn xóa collection cũ nếu đã tồn tại
        Args:
            vector_size: Kích thước của vector đặc trưng
            recreate_collection: Nếu True, xóa và tạo lại collection
        """
        try:
            # Kiểm tra xem collection đã tồn tại chưa
            collections = self.client.get_collections()
            collection_names = [collection.name for collection in collections.collections]

            if self.collection_name in collection_names and recreate_collection:
                # Xóa collection cũ nếu yêu cầu
                self.client.delete_collection(collection_name=self.collection_name)
                logger.info(f"Đã xóa collection cũ: {self.collection_name}")

            if self.collection_name not in collection_names or recreate_collection:
                # Tạo collection mới với cấu hình HNSW
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE,
                        on_disk=True  # Lưu vector trên đĩa để tiết kiệm RAM
                    ),
                    hnsw_config=models.HnswConfigDiff(
                        m=16,  # Số kết nối tối đa mỗi node
                        ef_construct=100,  # Số neighbor khi xây dựng chỉ mục
                        full_scan_threshold=10000  # Ngưỡng để dùng tìm kiếm toàn bộ
                    )
                )
                # Tạo range index cho trường id
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="id",
                    field_schema=models.PayloadSchemaType.INTEGER
                )
                # Tạo index cho trường file_name để tối ưu tìm kiếm chuỗi
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="file_name",
                    field_schema=models.PayloadSchemaType.KEYWORD
                )
                logger.info(
                    f"Đã tạo collection mới {self.collection_name} với vector size {vector_size}, range index cho id và keyword index cho file_name")
            else:
                logger.info(f"Collection {self.collection_name} đã tồn tại, tiếp tục sử dụng")
        except Exception as e:
            logger.error(f"Lỗi khi tạo collection: {str(e)}")
            raise

    def check_existing_files(self, file_paths: List[str]) -> List[str]:
        """
        Kiểm tra các file_path đã tồn tại trong collection
        Args:
            file_paths: Danh sách đường dẫn file cần kiểm tra
        Returns:
            Danh sách file_path đã tồn tại trong collection
        """
        try:
            existing_files = []
            for file_path in file_paths:
                # Tìm points có file_name khớp (dựa trên basename để tương thích)
                file_name = os.path.basename(file_path)
                result = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="file_name",
                                match=models.MatchValue(value=file_name)
                            )
                        ]
                    ),
                    limit=1,
                    with_payload=True
                )
                if result[0]:  # Nếu tìm thấy point
                    existing_files.append(file_path)
            return existing_files
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra file tồn tại: {str(e)}")
            raise

    def get_next_id(self) -> int:
        """
        Lấy ID lớn nhất hiện có trong collection và trả về ID tiếp theo
        Returns:
            ID tiếp theo để sử dụng
        """
        try:
            result = self.client.scroll(
                collection_name=self.collection_name,
                limit=1,
                order_by=models.OrderBy(
                    key="id",
                    direction="desc"
                )
            )
            points = result[0]
            if points:
                return points[0].id + 1
            return 0  # Bắt đầu từ 0 nếu collection rỗng
        except Exception as e:
            logger.error(f"Lỗi khi lấy ID tiếp theo: {str(e)}")
            raise

    def insert_vectors(self, feature_dict: Dict[str, Dict], recreate_collection: bool = False):
        """
        Chèn vectors vào Qdrant database
        Args:
            feature_dict: Dictionary với key là đường dẫn file, value là dict chứa vector và metadata
            recreate_collection: Nếu True, xóa và tạo lại collection trước khi chèn
        """
        try:
            if not feature_dict:
                logger.warning("Không có vectors để chèn")
                return
            # Lấy kích thước vector từ item đầu tiên
            first_item = next(iter(feature_dict.values()))
            vector_size = len(first_item["vector"])
            # Tạo collection (xóa nếu recreate_collection=True)
            self.create_collection(vector_size, recreate_collection=recreate_collection)
            # Kiểm tra file đã tồn tại (bỏ qua nếu recreate_collection=True)
            file_paths = list(feature_dict.keys())
            if recreate_collection:
                new_feature_dict = feature_dict  # Chèn tất cả vì collection đã được làm sạch
            else:
                existing_files = self.check_existing_files(file_paths)
                new_feature_dict = {k: v for k, v in feature_dict.items() if k not in existing_files}
                if existing_files:
                    logger.info(f"Bỏ qua {len(existing_files)} file đã tồn tại trong collection")
            if not new_feature_dict:
                logger.info("Không có file mới để chèn")
                return
            # Lấy ID bắt đầu
            start_id = self.get_next_id()
            # Chuẩn bị dữ liệu để chèn
            points = []
            for i, (file_path, data) in enumerate(new_feature_dict.items()):
                points.append(models.PointStruct(
                    id=start_id + i,
                    vector=data["vector"].tolist(),
                    payload={
                        "file_name": data["file_name"],
                        "file_type": data["file_type"],
                        "file_size_kb": float(data["file_size_kb"]),
                        "sample_rate": int(data["sample_rate"]),
                        "channel": int(data["channel"]),
                        "samples": int(data["samples"]),
                        "duration": float(data["duration"]),
                        "subtype": data["subtype"]
                    }
                ))
            # Thực hiện upsert (insert hoặc update)
            operation_info = self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Đã chèn {len(points)} vectors mới vào database")
            return operation_info
        except Exception as e:
            logger.error(f"Lỗi khi chèn vectors: {str(e)}")
            raise

    def search_similar(self, query_vector: np.ndarray, top_k: int = TOP_K) -> List[Dict[str, Any]]:
        """
        Tìm kiếm các vectors tương tự nhất
        Args:
            query_vector: Vector đặc trưng cần tìm kiếm
            top_k: Số lượng kết quả trả về
        Returns:
            Danh sách các file tương tự nhất kèm theo độ tương đồng
        """
        try:
            # Sửa lại cú pháp gọi API theo phiên bản Qdrant mới nhất
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.tolist(),
                limit=top_k
            )
            # Chuyển đổi kết quả thành định dạng dễ sử dụng hơn
            results = []
            for hit in search_results:
                results.append({
                    "file_name": hit.payload["file_name"],
                    "file_type": hit.payload["file_type"],
                    "file_size_kb": hit.payload["file_size_kb"],
                    "sample_rate": hit.payload["sample_rate"],
                    "channel": hit.payload["channel"],
                    "samples": hit.payload["samples"],
                    "duration": hit.payload["duration"],
                    "subtype": hit.payload["subtype"],
                    "similarity": hit.score
                })
            return results
        except Exception as e:
            logger.error(f"Lỗi khi tìm kiếm vectors tương tự: {str(e)}")
            raise

    def search_by_filename(self, query_string: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Tìm kiếm các vector có file_name chứa query_string (so sánh không phân biệt hoa/thường)
        Args:
            query_string: Chuỗi cần tìm trong file_name
            limit: Số lượng kết quả tối đa
        Returns:
            Danh sách các file khớp với query
        """
        try:
            # Tạo bộ lọc để tìm file_name chứa query_string
            # Lưu ý: Qdrant không hỗ trợ trực tiếp tìm kiếm substring với index KEYWORD,
            # nên ta dùng scroll với MatchText hoặc lấy tất cả và lọc phía client
            result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="file_name",
                            match=models.MatchText(text=query_string.upper())
                        )
                    ]
                ),
                limit=limit,
                with_payload=True
            )
            # Chuyển đổi kết quả
            results = []
            for point in result[0]:
                results.append({
                    "file_name": point.payload["file_name"],
                    "file_type": point.payload["file_type"],
                    "file_size_kb": point.payload["file_size_kb"],
                    "sample_rate": point.payload["sample_rate"],
                    "channel": point.payload["channel"],
                    "samples": point.payload["samples"],
                    "duration": point.payload["duration"],
                    "subtype": point.payload["subtype"],
                    "similarity": 1.0  # Giả định similarity = 1.0 vì là tìm kiếm chính xác
                })
            return results
        except Exception as e:
            logger.error(f"Lỗi khi tìm kiếm theo file_name: {str(e)}")
            raise

    def get_collection_info(self) -> Dict:
        """
            Lấy thông tin về collection
            Returns:
                Thông tin về collection
        """
        try:
            collection_info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": self.collection_name,
                "points_count": getattr(collection_info, 'points_count', 0),
                "status": collection_info.status
            }
        except UnexpectedResponse:
            # Collection không tồn tại
            return {"name": self.collection_name, "points_count": 0, "status": "không tồn tại"}
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin collection: {str(e)}")
            raise


