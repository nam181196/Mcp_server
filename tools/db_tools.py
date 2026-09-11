import os
import sys
import json

# Đảm bảo thư mục gốc dự án nằm trong sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db_service import db_service
from auth.oauth_provider import oauth_provider
from auth.scopes import has_required_scope

def _check_db_scope(required_scope: str) -> tuple:
    """
    Xác thực và kiểm tra scope DB. Trả về (auth_result, error_str).
    error_str là None nếu được phép, ngược lại là thông báo lỗi.
    """
    api_key = os.environ.get("MCP_API_KEY") or os.environ.get("BEARER_TOKEN")
    auth_result = oauth_provider.authenticate_request(api_key)

    if not auth_result.get("authenticated"):
        return auth_result, f"Lỗi xác thực (401 Unauthorized): {auth_result.get('error')}"

    if not has_required_scope(auth_result.get("scopes", []), required_scope):
        role = auth_result.get("role", "unknown")
        return auth_result, (
            f"Lỗi phân quyền (403 Forbidden): Role '{role}' không có quyền thực hiện thao tác này.\n"
            f"Scope yêu cầu: '{required_scope}'. Vui lòng kết nối bằng MCP Server Admin."
        )

    return auth_result, None


def register_db_tools(mcp):
    """Đăng ký các MCP Tools thao tác trực tiếp với Database MongoDB Atlas."""

    # ----------------------------------------------------------------
    # 1. XEM THỐNG KÊ DB - CHỈ ADMIN (scope: db:read)
    # ----------------------------------------------------------------
    @mcp.tool()
    def db_get_stats() -> str:
        """[ADMIN ONLY - DIRECT DB] Xem thống kê danh sách collections và số lượng bản ghi trong MongoDB."""
        _, err = _check_db_scope("db:read")
        if err:
            return err
        try:
            stats = db_service.get_collection_stats()
            return f"[MongoDB Direct Stats]\n{json.dumps(stats, indent=2, ensure_ascii=False)}"
        except Exception as e:
            return f"Lỗi kết nối MongoDB Direct: {str(e)}"

    # ----------------------------------------------------------------
    # 2. TÌM KIẾM DOCUMENT - CHỈ ADMIN (scope: db:read)
    # ----------------------------------------------------------------
    @mcp.tool()
    def db_find_documents(collection: str, filter_json: str = "{}", limit: int = 20) -> str:
        """[ADMIN ONLY - DIRECT DB] Truy vấn document trong MongoDB Collection theo filter JSON.

        Args:
            collection: Tên collection ('products', 'orders', 'users').
            filter_json: Điều kiện lọc JSON (vd: '{\"category\": \"Giày\"}' hoặc '{}').
            limit: Số lượng bản ghi tối đa (mặc định 20).
        """
        _, err = _check_db_scope("db:read")
        if err:
            return err
        try:
            filter_dict = json.loads(filter_json) if filter_json else {}
        except Exception as e:
            return f"Lỗi cú pháp filter_json: {str(e)}"
        try:
            docs = db_service.find_documents(collection, filter_dict=filter_dict, limit=limit)
            return f"[MongoDB Direct Query - Collection: '{collection}'] (Tìm thấy {len(docs)} bản ghi)\n{json.dumps(docs, indent=2, ensure_ascii=False)}"
        except Exception as e:
            return f"Lỗi khi truy vấn MongoDB collection '{collection}': {str(e)}"

    # ----------------------------------------------------------------
    # 3. THÊM DOCUMENT - CHỈ ADMIN (scope: db:insert)
    # ----------------------------------------------------------------
    @mcp.tool()
    def db_insert_document(collection: str, document_json: str) -> str:
        """[ADMIN ONLY - DIRECT DB] Thêm 1 document mới vào MongoDB Collection.

        Args:
            collection: Tên collection.
            document_json: Chuỗi JSON nội dung document cần thêm.
        """
        _, err = _check_db_scope("db:insert")
        if err:
            return err
        try:
            doc_dict = json.loads(document_json)
            result = db_service.insert_document(collection, doc_dict)
            return f"[MongoDB Direct Insert Success]\n{json.dumps(result, indent=2, ensure_ascii=False)}"
        except Exception as e:
            return f"Lỗi khi insert document vào collection '{collection}': {str(e)}"

    # ----------------------------------------------------------------
    # 4. CẬP NHẬT DOCUMENT - CHỈ ADMIN (scope: db:update)
    # ----------------------------------------------------------------
    @mcp.tool()
    def db_update_document(collection: str, filter_json: str, update_json: str) -> str:
        """[ADMIN ONLY - DIRECT DB] Cập nhật document trong MongoDB Collection theo filter.

        Args:
            collection: Tên collection.
            filter_json: Điều kiện lọc JSON (vd: '{\"name\": \"Áo khoác\"}').
            update_json: Dữ liệu cập nhật JSON (vd: '{\"price\": 500000}').
        """
        _, err = _check_db_scope("db:update")
        if err:
            return err
        try:
            filter_dict = json.loads(filter_json)
            update_dict = json.loads(update_json)
            result = db_service.update_document(collection, filter_dict, update_dict)
            return f"[MongoDB Direct Update Result]\n{json.dumps(result, indent=2, ensure_ascii=False)}"
        except Exception as e:
            return f"Lỗi khi update document trong collection '{collection}': {str(e)}"

    # ----------------------------------------------------------------
    # 5. XOÁ DOCUMENT - CHỈ ADMIN (scope: db:delete)
    # ----------------------------------------------------------------
    @mcp.tool()
    def db_delete_document(collection: str, filter_json: str) -> str:
        """[ADMIN ONLY - DIRECT DB] Xoá document khỏi MongoDB Collection theo filter.

        Args:
            collection: Tên collection.
            filter_json: Điều kiện lọc JSON (vd: '{\"_id\": \"abc123\"}').
        """
        _, err = _check_db_scope("db:delete")
        if err:
            return err
        try:
            filter_dict = json.loads(filter_json)
            result = db_service.delete_document(collection, filter_dict)
            return f"[MongoDB Direct Delete Result]\n{json.dumps(result, indent=2, ensure_ascii=False)}"
        except Exception as e:
            return f"Lỗi khi delete document khỏi collection '{collection}': {str(e)}"
