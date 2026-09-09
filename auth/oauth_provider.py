import os
from auth.token_service import verify_token, extract_role
from auth.user_service import get_webshop_token
from auth.scopes import get_scopes_for_role

# State lưu trữ session role động cho Single MCP Server instance (STDIO / In-Memory Session)
_CURRENT_ACTIVE_ROLE = os.environ.get("DEFAULT_MCP_ROLE", "user")

def set_active_role(role: str):
    """Đặt Role chủ động cho MCP Server Instance hiện tại."""
    global _CURRENT_ACTIVE_ROLE
    if role in ["admin", "user"]:
        _CURRENT_ACTIVE_ROLE = role

def get_active_role() -> str:
    """Lấy Role đang kích hoạt trong MCP Server Instance."""
    return _CURRENT_ACTIVE_ROLE

class OAuthProvider:
    """Quản lý luồng xác thực OAuth động cho 1 MCP Server duy nhất."""

    def _get_fallback_api_key(self) -> str:
        """
        Lấy token/key từ:
        1. Context Session Role hiện tại (_CURRENT_ACTIVE_ROLE)
        2. Hoặc biến môi trường MCP_API_KEY / BEARER_TOKEN
        """
        current_role = get_active_role()
        if current_role == "admin":
            return os.environ.get("MCP_ADMIN_KEY", "mcp_key_admin_test")
        elif current_role == "user":
            return os.environ.get("MCP_USER_KEY", "mcp_key_user_test")

        return os.environ.get("MCP_API_KEY") or os.environ.get("BEARER_TOKEN") or "mcp_key_user_test"

    def authenticate_request(self, token_or_key: str = None, ctx_headers: dict = None) -> dict:
        """
        Xác thực request đến từ MCP Client cho 1 MCP Server duy nhất.
        Thứ tự ưu tiên lấy Token/Identity:
        1. Context Headers (Authorization: Bearer <token>) từ MCP Host
        2. Tham số token_or_key truyền trực tiếp
        3. Active Session Role hiện tại của Server
        """
        # 1. Kiểm tra Token từ Header nếu có
        if ctx_headers:
            auth_header = ctx_headers.get("authorization") or ctx_headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token_or_key = auth_header.split("Bearer ")[1].strip()

        # 2. Fallback tự động lấy theo Active Session Role
        if not token_or_key or not str(token_or_key).strip():
            token_or_key = self._get_fallback_api_key()

        if not token_or_key or not str(token_or_key).strip():
            return {
                "authenticated": False,
                "error": "Chưa xác thực: Không tìm thấy Token/API Key trong request context hoặc session hiện tại."
            }

        token_str = str(token_or_key).strip()

        # Trường hợp A: JWT Token từ OAuth Provider (Clerk hoặc custom OAuth)
        if token_str.startswith("eyJ"):
            payload = verify_token(token_str)
            if not payload:
                return {"authenticated": False, "error": "JWT Token không hợp lệ hoặc đã hết hạn"}
            
            role = extract_role(payload)
            webshop_token = get_webshop_token(token_str, role)
            scopes = get_scopes_for_role(role)
            
            return {
                "authenticated": True,
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "role": role,
                "scopes": scopes,
                "webshop_token": webshop_token
            }

        # Trường hợp B: API Key giả lập (mcp_key_user_test, mcp_key_admin_test)
        webshop_token = get_webshop_token(token_str, None)
        if not webshop_token:
            return {"authenticated": False, "error": f"API Key '{token_str}' không hợp lệ"}

        role = "admin" if "admin" in token_str else "user"
        scopes = get_scopes_for_role(role)

        return {
            "authenticated": True,
            "user_id": token_str,
            "role": role,
            "scopes": scopes,
            "webshop_token": webshop_token
        }

oauth_provider = OAuthProvider()
