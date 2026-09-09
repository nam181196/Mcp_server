import os
import sys

# Đảm bảo thư mục gốc dự án nằm trong sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

# URL Gốc của Web Shop Backend (Express.js SportShop)
WEB_SHOP_BASE_URL = os.environ.get("WEB_SHOP_BASE_URL", "http://localhost:3000")

# Đường dẫn file mapping API Key
API_KEY_MAP_FILE = os.environ.get("API_KEY_MAP_FILE", os.path.join(os.path.dirname(__file__), "api_key_map.json"))

# Danh sách ánh xạ mặc định giữa MCP Client API Key và Session Cookie của Web Shop
DEFAULT_API_KEY_MAP = {
    "mcp_key_user_test": {
        "role": "user",
        "description": "Tài khoản User thường",
        "access_token": os.environ.get("WEB_SHOP_USER_TOKEN", "connect.sid=s%3AT7a4iR8Nh8FicBDA2GKeHUwtQt4Ifm_e.aaOvPzqeJKGwDJhpgNG2qq87niK%2F3ZDl8FTP%2BXwQ6II")
    },
    "mcp_key_admin_test": {
        "role": "admin",
        "description": "Tài khoản Quản trị viên (Admin)",
        "access_token": os.environ.get("WEB_SHOP_ADMIN_TOKEN", "connect.sid=s%3AV3OPZitjk_-6egsz3kuGee7liXSs_OO4.XVwh80DryJ0vfkQ081FaA6g5Gl%2FWd449Mpv7OiNtst4")
    }
}

def load_api_key_map() -> dict:
    """Đọc cấu hình ánh xạ API Key từ file JSON nếu có, nếu không sử dụng mặc định."""
    if os.path.exists(API_KEY_MAP_FILE):
        try:
            with open(API_KEY_MAP_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Warning] Không thể đọc file mapping API Key: {e}. Sử dụng cấu hình mặc định.")
    return DEFAULT_API_KEY_MAP

def get_token_for_api_key(api_key: str) -> dict:
    """Tra cứu Access Token / Session Cookie từ API Key của MCP Client.
    
    Returns:
        dict chứa 'access_token' và 'role' hoặc None nếu API Key không hợp lệ.
    """
    key_map = load_api_key_map()
    return key_map.get(api_key.strip())
