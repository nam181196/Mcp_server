import os
from auth.token_service import verify_token, extract_role
from auth.user_service import get_webshop_token
from auth.scopes import get_scopes_for_role

class OAuthProvider:
    """Quản lý luồng xác thực OAuth cho MCP Server."""

    def _get_fallback_api_key() -> str:
        """Lấy token/key từ biến môi trường của tiến trình MCP Server."""
        return os.environ.get("MCP_API_KEY") or os.environ.get("BEARER_TOKEN")

    def authenticate_request(self, token_or_key: str = None) -> dict:
        """
        Xác thực request đến từ MCP Client.
        Nếu token_or_key không truyền vào, tự động lấy từ biến môi trường MCP_API_KEY.
        """
        if not token_or_key or not str(token_or_key).strip():
            token_or_key = OAuthProvider._get_fallback_api_key()

        if not token_or_key or not str(token_or_key).strip():
            return {
                "authenticated": False,
                "error": "Chưa xác thực: Không tìm thấy Token/API Key trong câu lệnh hoặc trong cấu hình môi trường MCP_API_KEY."
            }

        token_str = str(token_or_key).strip()

        # Trường hợp 1: JWT Token từ OAuth Provider (Clerk hoặc custom OAuth)
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

        # Trường hợp 2: API Key giả lập (mcp_key_user_test, mcp_key_admin_test)
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
