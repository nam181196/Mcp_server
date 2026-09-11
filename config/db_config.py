import os
import sys

# Đảm bảo thư mục gốc dự án nằm trong sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Tự động đọc file .env ở thư mục gốc nếu chưa được nạp vào os.environ
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(env_path):
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() not in os.environ:
                        os.environ[k.strip()] = v.strip()
    except Exception as e:
        print(f"[Warning] Không thể đọc file .env: {e}")

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017")
MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME", "sportshop")
ENABLE_DB_FALLBACK = os.environ.get("ENABLE_DB_FALLBACK", "true").lower() in ("true", "1", "yes")
