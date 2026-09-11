import os

# Cấu hình Issuer & JWKS URL cho OAuth Server độc lập (Generic OAuth Provider / Local Auth)
OAUTH_ISSUER = os.environ.get("OAUTH_ISSUER", "http://localhost:8000").rstrip("/")
JWKS_URL = os.environ.get("JWKS_URL", f"{OAUTH_ISSUER}/.well-known/jwks.json")

# Danh sách Scopes phân quyền theo Role
DEFAULT_SCOPES = {
    "user": [
        # Sản phẩm: chỉ đọc công khai
        "products:read",
        # Đơn hàng: chỉ xem và tạo của chính mình
        "orders:read_own",
        "orders:create_own",
    ],
    "admin": [
        # Sản phẩm: toàn quyền qua WebShop API
        "products:read", "products:create", "products:update", "products:delete",
        # Đơn hàng: toàn quyền qua WebShop API
        "orders:read_all", "orders:read_own", "orders:create_own", "orders:stats",
        # Người dùng: toàn quyền
        "users:read_all",
        # DB trực tiếp: toàn quyền CRUD trên MongoDB Atlas
        "db:read", "db:insert", "db:update", "db:delete",
    ]
}
