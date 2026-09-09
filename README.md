# WebShop MCP Server (Proxy & OAuth-enabled)

MCP Server đóng vai trò Gateway kết nối MCP Client (Cursor, Claude Desktop, ChatGPT) tới **WebShop Backend API** (Express.js / Node.js). 
Hỗ trợ cơ chế phân quyền RBAC (Role-Based Access Control) cho User và Admin dựa trên OAuth JWT hoặc API Key.

---

## 🛠 Cấu hình sử dụng trên MCP Client (Cursor / Claude Desktop)

Người dùng không cần truyền thủ công `api_key` trong mỗi câu prompt. Thay vào đó, bạn cấu hình 2 instance MCP Server trong file `mcp.json` tương ứng với từng Role:

```json
{
  "mcpServers": {
    "SportShop_Admin": {
      "command": "/Users/nam/Desktop/MCP_server/venv_new/bin/python3",
      "args": [
        "/Users/nam/Desktop/MCP_server/server.py"
      ],
      "env": {
        "MCP_API_KEY": "mcp_key_admin_test"
      }
    },
    "SportShop_User": {
      "command": "/Users/nam/Desktop/MCP_server/venv_new/bin/python3",
      "args": [
        "/Users/nam/Desktop/MCP_server/server.py"
      ],
      "env": {
        "MCP_API_KEY": "mcp_key_user_test"
      }
    }
  }
}
```

---

## 💬 Ví dụ câu lệnh Prompt chuẩn (Không cần truyền `api_key`)

### Dành cho Admin (`SportShop_Admin`):
- *"Lấy tất cả đơn hàng trong hệ thống giúp tôi."*
- *"Xem thống kê doanh thu và báo cáo tổng quan đơn hàng."*
- *"Thêm sản phẩm mới tên 'Giày Chạy Bộ Nike Air Zoom', giá 2500000, thuộc danh mục 'Giày', thương hiệu 'Nike'."*

### Dành cho User (`SportShop_User`):
- *"Cho tôi xem danh sách sản phẩm đang bán thuộc danh mục Giày."*
- *"Xem danh sách các đơn hàng cá nhân của tôi."*
- *"Tạo đơn hàng mua 2 sản phẩm ID P01."*

---

## 🏗 Kiến trúc thư mục dự án

```text
MCP_server/
├── auth/
│   ├── oauth_provider.py      ← Xác thực Token & fallback tự lấy MCP_API_KEY từ env
│   ├── user_service.py        ← Ánh xạ tài khoản OAuth sang WebShop Backend Token
│   ├── token_service.py       ← Xác minh & đọc JWT Token
│   └── scopes.py              ← Định nghĩa & kiểm tra Scope cho Role (admin / user)
├── config/
│   ├── auth_config.py         ← Cấu hình Issuer & mặc định Scopes
│   └── web_shop_config.py     ← URL Backend & API Key mappings
├── services/
│   └── web_shop_client.py     ← Client gửi HTTP Request tới WebShop Backend API
├── tools/
│   └── web_shop_tools.py      ← Đăng ký MCP Tools (api_key là tùy chọn)
└── server.py                  ← Server entrypoint (STDIO / HTTP / SSE)
```
