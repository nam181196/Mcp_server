import os
import sys

# Đảm bảo thư mục gốc dự án nằm trong sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pyrefly: ignore [missing-import]
import httpx
import json
from config.web_shop_config import WEB_SHOP_BASE_URL
from config.db_config import ENABLE_DB_FALLBACK
from services.db_service import db_service
from auth.oauth_provider import oauth_provider
from auth.scopes import has_required_scope

class WebShopClient:
    """Client kết nối tới Web Shop Backend API thông qua OAuthProvider."""

    def __init__(self, base_url: str = None):
        self.base_url = (base_url or WEB_SHOP_BASE_URL).rstrip("/")

    def request(
        self,
        method: str,
        endpoint: str,
        api_key: str = None,
        required_scope: str = None,
        data: dict = None,
        params: dict = None
    ) -> str:
        """
        Thực hiện HTTP Request tới Web Shop API sau khi xác thực và kiểm tra Scope từ OAuthProvider.
        Nếu api_key là None, OAuthProvider sẽ tự động sử dụng MCP_API_KEY từ biến môi trường.
        """
        # 1. Xác thực qua OAuthProvider (Tự động lấy token nếu api_key=None)
        auth_result = oauth_provider.authenticate_request(api_key)
        if not auth_result.get("authenticated"):
            return f"Lỗi xác thực MCP (401 Unauthorized): {auth_result.get('error')}"

        # 2. Kiểm tra Scope (nếu có yêu cầu)
        if required_scope and not has_required_scope(auth_result.get("scopes", []), required_scope):
            return f"Lỗi phân quyền MCP (403 Forbidden): Quyền hạn của bạn ({auth_result.get('role')}) thiếu scope '{required_scope}'."

        access_token = auth_result.get("webshop_token")
        headers = {
            "X-API-Key": access_token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"

        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    json=data,
                    params=params
                )
                if response.status_code >= 500 and ENABLE_DB_FALLBACK and db_service.is_connected():
                    fallback_res = db_service.handle_fallback_request(method, endpoint, data=data, params=params)
                    return (
                        f"[Fallback DB Mode - MongoDB Direct Connection]\n"
                        f"Thông báo: Web Shop Backend API ({self.base_url}) trả về lỗi hệ thống ({response.status_code}).\n"
                        f"Hệ thống đã tự động chuyển sang truy vấn trực tiếp Database MongoDB:\n\n"
                        f"{fallback_res}"
                    )
                return self._format_response(response, endpoint)


        except (httpx.ConnectError, httpx.TimeoutException) as e:
            if ENABLE_DB_FALLBACK and db_service.is_connected():
                fallback_res = db_service.handle_fallback_request(method, endpoint, data=data, params=params)
                return (
                    f"[Fallback DB Mode - MongoDB Direct Connection]\n"
                    f"Thông báo: Web Shop Backend API ({self.base_url}) không khả dụng ({type(e).__name__}).\n"
                    f"Hệ thống đã tự động chuyển sang truy vấn trực tiếp Database MongoDB:\n\n"
                    f"{fallback_res}"
                )
            return (
                f"Lỗi kết nối Web Shop (503 Service Unavailable):\n"
                f"Không thể kết nối tới Web Shop Backend tại địa chỉ: {self.base_url}\n"
                f"Vui lòng kiểm tra xem Web Shop Backend Server đã được khởi chạy chưa."
            )
        except Exception as e:
            return f"Lỗi không xác định khi kết nối Web Shop API: {str(e)}"


    def _format_response(self, response: httpx.Response, endpoint: str) -> str:
        status_code = response.status_code

        try:
            body_data = response.json()
            body_str = json.dumps(body_data, indent=2, ensure_ascii=False)
        except Exception:
            body_str = response.text

        if 200 <= status_code < 300:
            return f"[Web Shop Response - {status_code} OK]\n{body_str}"
        elif status_code == 401:
            return (
                f"[Web Shop Backend Response - 401 Unauthorized]\n"
                f"Mô tả: Web Shop Backend từ chối Token/Cookie Session.\n"
                f"Nội dung:\n{body_str}"
            )
        elif status_code == 403:
            return (
                f"[Web Shop Backend Response - 403 Forbidden]\n"
                f"Mô tả: Web Shop Backend từ chối quyền truy cập (Role không đủ quyền).\n"
                f"Nội dung:\n{body_str}"
            )
        elif status_code == 404:
            return (
                f"[Web Shop Backend Response - 404 Not Found]\n"
                f"Mô tả: Không tìm thấy tài nguyên tại endpoint '{endpoint}'.\n"
                f"Nội dung:\n{body_str}"
            )
        else:
            return (
                f"[Web Shop Backend Response - {status_code}]\n"
                f"Nội dung:\n{body_str}"
            )

web_shop_client = WebShopClient()
