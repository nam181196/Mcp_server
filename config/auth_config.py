import os

# Cấu hình Issuer & JWKS URL cho OAuth Server độc lập (Generic OAuth Provider / Local Auth)
OAUTH_ISSUER = os.environ.get("OAUTH_ISSUER", "http://localhost:8000").rstrip("/")
JWKS_URL = os.environ.get("JWKS_URL", f"{OAUTH_ISSUER}/.well-known/jwks.json")

# Danh sách Scopes mặc định phân quyền theo Role
DEFAULT_SCOPES = {
    "user": ["products:read", "orders:read_own", "orders:create_own"],
    "admin": [
        "products:read", "products:create", "products:update", "products:delete",
        "orders:read_all", "orders:stats", "users:read_all"
    ]
}
