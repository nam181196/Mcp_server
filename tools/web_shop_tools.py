import os
import sys

# Đảm bảo thư mục gốc dự án nằm trong sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pyrefly: ignore [missing-import]
from services.web_shop_client import web_shop_client
# pyrefly: ignore [missing-import]
from auth.oauth_provider import set_active_role, get_active_role

def register_web_shop_tools(mcp):
    """Đăng ký các MCP Tools cho 1 MCP Server duy nhất (Hỗ trợ đổi Role và tự nhận diện động)."""

    # -------------------------------------------------------------
    # 0. MANAGEMENT TOOL CHO SINGLE MCP SERVER INSTANCE
    # -------------------------------------------------------------
    @mcp.tool()
    def switch_mcp_role(role: str) -> str:
        """Chuyển đổi Role cho MCP Server hiện tại (Cho phép 'admin' hoặc 'user').

        Args:
            role: Tên role cần chuyển ('admin' hoặc 'user').
        """
        role_clean = role.lower().strip()
        if role_clean not in ["admin", "user"]:
            return f"Lỗi: Role '{role}' không hợp lệ. Chỉ chấp nhận 'admin' hoặc 'user'."
        set_active_role(role_clean)
        return f"Thành công: Đã chuyển Role của MCP Server hiện tại sang '{role_clean}'. Các câu lệnh tiếp theo sẽ sử dụng quyền này."

    @mcp.tool()
    def get_current_mcp_status() -> str:
        """Xem trạng thái Role hiện tại và quyền hạn của MCP Server."""
        current_role = get_active_role()
        return f"[MCP Server Status]\nRole hiện tại: '{current_role}'\nĐã sẵn sàng nhận các câu lệnh không cần api_key."

    # -------------------------------------------------------------
    # 1. TÁC VỤ DÀNH CHO USER THƯỜNG / CÔNG KHAI (USER ROLE)
    # -------------------------------------------------------------

    @mcp.tool()
    def get_web_shop_products(category: str = None, api_key: str = None) -> str:
        """Lấy danh sách tất cả sản phẩm từ Web Shop."""
        params = {}
        if category:
            params["category"] = category
        return web_shop_client.request("GET", "/products", api_key=api_key, required_scope="products:read", params=params)

    @mcp.tool()
    def get_product_detail(product_id: str, api_key: str = None) -> str:
        """Xem thông tin chi tiết một sản phẩm theo ID."""
        return web_shop_client.request("GET", f"/products/{product_id}", api_key=api_key, required_scope="products:read")

    @mcp.tool()
    def get_my_orders(api_key: str = None) -> str:
        """Xem danh sách đơn hàng cá nhân của tôi."""
        return web_shop_client.request("GET", "/my-orders", api_key=api_key, required_scope="orders:read_own")

    @mcp.tool()
    def get_order_detail(order_id: str, api_key: str = None) -> str:
        """Xem chi tiết một đơn hàng."""
        return web_shop_client.request("GET", f"/orders/{order_id}", api_key=api_key, required_scope="orders:read_own")

    @mcp.tool()
    def create_order(items_json_str: str, api_key: str = None) -> str:
        """Tạo đơn hàng mới trên Web Shop."""
        try:
            items_data = json.loads(items_json_str)
        except Exception:
            items_data = items_json_str

        payload = {"items": items_data}
        return web_shop_client.request("POST", "/orders", api_key=api_key, required_scope="orders:create_own", data=payload)

    # -------------------------------------------------------------
    # 2. TÁC VỤ DÀNH RIÊNG CHO QUẢN TRỊ VIÊN (ADMIN ROLE ONLY)
    # -------------------------------------------------------------

    @mcp.tool()
    def admin_get_all_orders(api_key: str = None) -> str:
        """[ADMIN ONLY] Quản trị viên xem tất cả đơn hàng trong toàn bộ hệ thống."""
        return web_shop_client.request("GET", "/orders", api_key=api_key, required_scope="orders:read_all")

    @mcp.tool()
    def admin_get_order_stats(api_key: str = None) -> str:
        """[ADMIN ONLY] Quản trị viên xem báo cáo thống kê doanh thu, số lượng đơn."""
        return web_shop_client.request("GET", "/orders/stats", api_key=api_key, required_scope="orders:stats")

    @mcp.tool()
    def admin_get_all_users(api_key: str = None) -> str:
        """[ADMIN ONLY] Quản trị viên xem danh sách tất cả tài khoản người dùng."""
        return web_shop_client.request("GET", "/users", api_key=api_key, required_scope="users:read_all")

    @mcp.tool()
    def admin_create_product(
        name: str,
        price: float,
        category: str,
        brand: str,
        description: str = "",
        image: str = "",
        api_key: str = None
    ) -> str:
        """[ADMIN ONLY] Quản trị viên thêm một sản phẩm mới vào Database."""
        payload = {
            "name": name,
            "price": price,
            "category": category,
            "brand": brand,
            "description": description,
            "image": image
        }
        return web_shop_client.request("POST", "/products", api_key=api_key, required_scope="products:create", data=payload)

    @mcp.tool()
    def admin_update_product(
        product_id: str,
        name: str = None,
        price: float = None,
        category: str = None,
        brand: str = None,
        description: str = None,
        image: str = None,
        api_key: str = None
    ) -> str:
        """[ADMIN ONLY] Quản trị viên cập nhật thông tin một sản phẩm."""
        payload = {}
        if name is not None: payload["name"] = name
        if price is not None: payload["price"] = price
        if category is not None: payload["category"] = category
        if brand is not None: payload["brand"] = brand
        if description is not None: payload["description"] = description
        if image is not None: payload["image"] = image

        return web_shop_client.request("PUT", f"/products/{product_id}", api_key=api_key, required_scope="products:update", data=payload)

    @mcp.tool()
    def admin_delete_product(product_id: str, api_key: str = None) -> str:
        """[ADMIN ONLY] Quản trị viên xoá một sản phẩm khỏi Database."""
        return web_shop_client.request("DELETE", f"/products/{product_id}", api_key=api_key, required_scope="products:delete")
