# 🛒 Web Shop MCP Server Proxy - Hướng Dẫn Chi Tiết Từ A Đến Z

Tài liệu này ghi lại **từng bước chi tiết** từ quá trình khởi tạo môi trường, cài đặt thư viện, xây dựng cấu trúc dự án, lập trình các module core proxy đến cách khởi chạy và kiểm thử MCP Server kết nối với Web Shop Backend API.

---

## 📌 BƯỚC 1: KHỞI TẠO DỰ ÁN & MÔI TRƯỜNG ẢO (VIRTUAL ENVIRONMENT)

1. **Di chuyển vào thư mục dự án**:
   ```bash
   cd "/Users/nam/Desktop/MCP server"
   ```

2. **Tạo Môi trường ảo Python (`venv`) mới**:
   ```bash
   python3 -m venv venv
   ```

3. **Kích hoạt Môi trường ảo**:
   - Trên macOS / Linux:
     ```bash
     source venv/bin/activate
     ```

---

## 📌 BƯỚC 2: CÀI ĐẶT CÁC THƯ VIỆN CẦN THIẾT (DOWNLOAD & INSTALL DEPENDENCIES)

1. **Tạo tệp `requirements.txt`**:
   ```text
   fastmcp>=0.1.0
   psutil>=5.9.0
   httpx>=0.27.0
   ```

2. **Chạy lệnh cài đặt thư viện**:
   ```bash
   ./venv/bin/pip install -r requirements.txt
   ```

---

## 📌 BƯỚC 3: XÂY DỰNG CẤU TRÚC THƯ MỤC DỰ ÁN (PROJECT STRUCTURE)

Tạo cấu trúc các gói package chuyên nghiệp như sau:
```text
MCP server/
├── server.py                   # Entry point chính của MCP Server (STDIO & SSE)
├── requirements.txt            # Thư viện phụ thuộc (fastmcp, httpx, psutil)
├── README.md                   # Hướng dẫn chi tiết từng bước làm
├── config/
│   ├── __init__.py
│   ├── web_shop_config.py      # Cấu hình Web Shop Base URL & tra cứu API Key
│   └── api_key_map.json        # Ánh xạ API Key MCP Client -> Access Token Web Shop
├── services/
│   ├── __init__.py
│   └── web_shop_client.py      # HTTP Client gửi request kèm Bearer Token & format lỗi
└── tools/
    ├── __init__.py
    └── web_shop_tools.py       # Đăng ký các MCP Tools (User Role & Admin Role)
```

---

## 📌 BƯỚC 4: LẬP TRÌNH CÁC MODULE CORE PROXY

### 1. Cấu hình Ánh Xạ API Key (`config/web_shop_config.py` & `config/api_key_map.json`)
- Ánh xạ `mcp_key_user_test` ➔ Web Shop User Access Token (Quyền User).
- Ánh xạ `mcp_key_admin_test` ➔ Web Shop Admin Access Token (Quyền Admin).

### 2. Service Gọi Web Shop API (`services/web_shop_client.py`)
- Nhận `api_key` từ MCP Client.
- Gửi HTTP Request sang Web Shop Backend kèm header `Authorization: Bearer <Web_Shop_Access_Token>`.
- Chuyển đổi phản hồi hoặc mã lỗi HTTP (`401 Unauthorized`, `403 Forbidden`, `404 Not Found`) từ Web Shop Backend thành thông điệp MCP Error thân thiện.

### 3. Đăng ký MCP Tools (`tools/web_shop_tools.py`)
- **Tác vụ User thường**: `get_web_shop_products`, `get_product_detail`, `get_my_orders`, `get_order_detail`, `create_order`.
- **Tác vụ Admin**: `admin_get_all_orders`, `admin_update_order_status`, `admin_get_all_users`.

### 4. Entry Point Khởi Chạy (`server.py`)
- Đăng ký các Tools vào FastMCP.
- Hỗ trợ truyền tải giao thức qua `STDIO` và `Streamable HTTP (SSE)`.

---

## 📌 BƯỚC 5: HƯỚNG DẪN KHỞI CHẠY & KIỂM THỬ (RUN & TEST)

### 1. Khởi chạy mặc định giao thức STDIO (Cho Claude Desktop / Cursor):
```bash
./venv/bin/python3 server.py
```

### 2. Khởi chạy giao thức Streamable HTTP (SSE) (Cho Remote Client / Web):
```bash
MCP_TRANSPORT=sse MCP_PORT=8000 ./venv/bin/python3 server.py
```
Server SSE sẽ lắng nghe tại địa chỉ: `http://localhost:8000/sse`

### 3. Cấu hình Claude Desktop (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "web-shop-mcp-server": {
      "command": "/Users/nam/Desktop/MCP server/venv/bin/python3",
      "args": [
        "/Users/nam/Desktop/MCP server/server.py"
      ]
    }
  }
}
```
