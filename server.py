import os
import sys

# Đảm bảo thư mục gốc dự án nằm trong sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# pyrefly: ignore [missing-import]
from fastmcp import FastMCP
# pyrefly: ignore [missing-import]
from tools.web_shop_tools import register_web_shop_tools
from tools.db_tools import register_db_tools
from config.auth_config import OAUTH_ISSUER, JWKS_URL

# Khởi tạo FastMCP Server cốt lõi cho Web Shop Proxy API
mcp = FastMCP("web-shop-mcp-server")

# Đăng ký các Web Shop API Proxy Tools và Direct Database Tools
register_web_shop_tools(mcp)
register_db_tools(mcp)


# -----------------------------------------------------------------------------
# OAUTH & OPENID DISCOVERY ENDPOINTS (Generic OAuth / Custom Provider)
# -----------------------------------------------------------------------------
# pyrefly: ignore [missing-import]
from starlette.responses import JSONResponse
# pyrefly: ignore [missing-import]
from starlette.requests import Request

OAUTH_SERVER_METADATA = {
    "issuer": OAUTH_ISSUER,
    "authorization_endpoint": f"{OAUTH_ISSUER}/oauth/authorize",
    "token_endpoint": f"{OAUTH_ISSUER}/oauth/token",
    "revocation_endpoint": f"{OAUTH_ISSUER}/oauth/token/revoke",
    "userinfo_endpoint": f"{OAUTH_ISSUER}/oauth/userinfo",
    "jwks_uri": JWKS_URL,
    "scopes_supported": ["openid", "email", "profile", "public_metadata", "offline_access"],
    "response_types_supported": ["code"],
    "grant_types_supported": ["authorization_code", "refresh_token"],
    "code_challenge_methods_supported": ["S256"]
}

PROTECTED_RESOURCE_METADATA = {
    "authorization_servers": [OAUTH_ISSUER],
    "scopes_supported": ["openid", "email", "profile", "public_metadata", "offline_access"],
    "bearer_methods_supported": ["header"]
}

# Đăng ký các route Discovery cho cả root và subpath /mcp
for path in [
    "/.well-known/oauth-authorization-server",
    "/.well-known/openid-configuration",
    "/mcp/.well-known/oauth-authorization-server",
    "/mcp/.well-known/openid-configuration",
    "/.well-known/oauth-authorization-server/mcp",
    "/.well-known/openid-configuration/mcp",
]:
    @mcp.custom_route(path, methods=["GET"])
    async def oauth_metadata_handler(request: Request, p=path):
        return JSONResponse(OAUTH_SERVER_METADATA)

for path in [
    "/.well-known/oauth-protected-resource",
    "/mcp/.well-known/oauth-protected-resource",
    "/.well-known/oauth-protected-resource/mcp",
]:
    @mcp.custom_route(path, methods=["GET"])
    async def resource_metadata_handler(request: Request, p=path):
        return JSONResponse(PROTECTED_RESOURCE_METADATA)

if __name__ == "__main__":
    # Cấu hình giao thức truyền tải từ biến môi trường
    # Mặc định: stdio (Claude Desktop / Cursor)
    # Tùy chọn: http  (Streamable HTTP - ChatGPT Desktop, remote clients)
    # Tùy chọn: sse   (Legacy SSE - các client cũ)
    transport = os.environ.get("MCP_TRANSPORT", "stdio").lower()
    port = int(os.environ.get("MCP_PORT", 8000))
    host = os.environ.get("MCP_HOST", "0.0.0.0")

    if transport == "http":
        print(f"[INFO] Khởi chạy MCP Server qua Streamable HTTP tại http://{host}:{port}/mcp ...")
        mcp.run(transport="http", port=port, host=host)
    elif transport == "sse":
        print(f"[INFO] Khởi chạy MCP Server qua Legacy SSE tại http://{host}:{port}/sse ...")
        mcp.run(transport="sse", port=port, host=host)
    else:
        # Khởi chạy mặc định qua giao thức STDIO (dùng cho Claude Desktop / Cursor)
        mcp.run()
