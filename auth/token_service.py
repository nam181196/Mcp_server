import os
# pyrefly: ignore [missing-import]
import jwt
# pyrefly: ignore [missing-import]
from jwt import PyJWKClient
from config.auth_config import JWKS_URL, OAUTH_ISSUER

# Khởi tạo JWKS Client nếu sử dụng Remote JWKS
jwks_client = None

def get_jwks_client():
    global jwks_client
    if jwks_client is None and JWKS_URL.startswith("http"):
        try:
            jwks_client = PyJWKClient(JWKS_URL)
        except Exception as e:
            print(f"[TokenService] Không thể kết nối JWKS URL: {e}")
    return jwks_client

def verify_token(token: str) -> dict:
    """Xác minh và giải mã JWT token."""
    if not token:
        return None
    try:
        client = get_jwks_client()
        if client:
            signing_key = client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_aud": False}
            )
            return payload
        else:
            # Fallback decode không kiểm tra chữ ký nếu chạy chế độ Local Dev (Secret key)
            secret_key = os.environ.get("JWT_SECRET_KEY", "mcp_jwt_secret_dev_key")
            payload = jwt.decode(token, secret_key, algorithms=["HS256"], options={"verify_aud": False})
            return payload
    except Exception as e:
        print(f"[TokenService Error] Verify token failed: {e}")
        return None

def extract_role(payload: dict) -> str:
    """Trích xuất role từ payload của JWT."""
    if not payload:
        return "user"
    if "role" in payload:
        return payload["role"]
    metadata = payload.get("public_metadata") or payload.get("metadata") or {}
    if isinstance(metadata, dict) and "role" in metadata:
        return metadata["role"]
    return "user"
