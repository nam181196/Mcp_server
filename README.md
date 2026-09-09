# Single MCP Server Configuration & Usage Guide

MCP Server này cho phép chạy **duy nhất 1 MCP Server instance** để tự động phục vụ cả 2 Role (User và Admin).

---

## 🛠 Cấu hình trong `mcp.json` (Chỉ cần 1 MCP Server duy nhất)

```json
{
  "mcpServers": {
    "SportShop": {
      "command": "/Users/nam/Desktop/MCP_server/venv_new/bin/python3",
      "args": [
        "/Users/nam/Desktop/MCP_server/server.py"
      ],
      "env": {
        "DEFAULT_MCP_ROLE": "admin"
      }
    }
  }
}
```

---

## 💬 Các cách sử dụng linh hoạt trên 1 MCP Server

### Cách 1: Sử dụng mặc định (Không cần `api_key`)
- Chat trực tiếp: *"Lấy danh sách tất cả đơn hàng giúp tôi"* (Server sẽ dùng Role mặc định trong cấu hình).

### Cách 2: Chuyển đổi Role linh hoạt trong cùng 1 phiên chat
- Chat: *"Chuyển sang quyền user giúp tôi"* -> Server kích hoạt `switch_mcp_role(role="user")`.
- Chat: *"Chuyển sang quyền admin"* -> Server kích hoạt `switch_mcp_role(role="admin")`.

### Cách 3: Truyền OAuth Bearer Token tự động từ MCP Host Context
- Server tự trích xuất `Authorization: Bearer <Token>` từ Request Header của MCP Host để phân quyền theo từng câu lệnh.
