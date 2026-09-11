import os
import sys
import json

# Đảm bảo thư mục gốc dự án nằm trong sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.web_shop_client import web_shop_client

def register_web_shop_tools(mcp):
    """Đăng ký các MCP Tools tương tác với Web Shop API với phân quyền Scope chuẩn."""

    # ----------------------------------------------------------------
    # 1. DÀNH CHO USER THƯỜNG (User & Admin đều dùng được)
    # ----------------------------------------------------------------

    @mcp.tool()
    def get_web_shop_products(category: str = None, api_key: str = None) -> str:
        """Lấy danh sách tất cả sản phẩm từ Web Shop.

        Args:
            category: (Tùy chọn) Lọc theo danh mục sản phẩm.
            api_key: (Tùy chọn) Override API Key nếu không dùng môi trường mặc định.
        """
        params = {}
        if category:
            params["category"] = category
        return web_shop_client.request("GET", "/products", api_key=api_key,
                                       required_scope="products:read", params=params)

    @mcp.tool()
    def get_product_detail(product_id: str, api_key: str = None) -> str:
        """Xem thông tin chi tiết một sản phẩm theo ID.

        Args:
            product_id: Mã ID sản phẩm cần xem.
            api_key: (Tùy chọn) Override API Key.
        """
        return web_shop_client.request("GET", f"/products/{product_id}", api_key=api_key,
                                       required_scope="products:read")

    @mcp.tool()
    def get_my_orders(api_key: str = None) -> str:
        """Xem danh sách đơn hàng cá nhân của tôi."""
        return web_shop_client.request("GET", "/my-orders", api_key=api_key,
                                       required_scope="orders:read_own")

    @mcp.tool()
    def get_order_detail(order_id: str, api_key: str = None) -> str:
        """Xem chi tiết một đơn hàng cá nhân.

        Args:
            order_id: Mã đơn hàng cần xem.
            api_key: (Tùy chọn) Override API Key.
        """
        return web_shop_client.request("GET", f"/orders/{order_id}", api_key=api_key,
                                       required_scope="orders:read_own")

    @mcp.tool()
    def create_order(items_json_str: str, api_key: str = None) -> str:
        """Tạo đơn hàng mới trên Web Shop.

        Args:
            items_json_str: Chuỗi JSON danh sách sản phẩm (vd: '[{"product_id": "P01", "quantity": 2}]').
            api_key: (Tùy chọn) Override API Key.
        """
        try:
            items_data = json.loads(items_json_str)
        except Exception:
            items_data = items_json_str

        payload = {"items": items_data}
        return web_shop_client.request("POST", "/orders", api_key=api_key,
                                       required_scope="orders:create_own", data=payload)

    # ----------------------------------------------------------------
    # 2. DÀNH RIÊNG CHO ADMIN (scope kiểm tra nghiêm ngặt tại MCP Server)
    # ----------------------------------------------------------------

    @mcp.tool()
    def admin_get_all_orders(api_key: str = None) -> str:
        """[ADMIN ONLY] Quản trị viên xem tất cả đơn hàng trong hệ thống."""
        return web_shop_client.request("GET", "/orders", api_key=api_key,
                                       required_scope="orders:read_all")

    @mcp.tool()
    def admin_get_order_stats(api_key: str = None) -> str:
        """[ADMIN ONLY] Quản trị viên xem báo cáo thống kê doanh thu và đơn hàng."""
        return web_shop_client.request("GET", "/orders/stats", api_key=api_key,
                                       required_scope="orders:stats")

    @mcp.tool()
    def admin_get_all_users(api_key: str = None) -> str:
        """[ADMIN ONLY] Quản trị viên xem danh sách tất cả tài khoản người dùng."""
        return web_shop_client.request("GET", "/users", api_key=api_key,
                                       required_scope="users:read_all")

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
        """[ADMIN ONLY] Quản trị viên thêm một sản phẩm mới vào hệ thống.

        Args:
            name: Tên sản phẩm.
            price: Giá bán sản phẩm.
            category: Danh mục sản phẩm.
            brand: Thương hiệu.
            description: (Tùy chọn) Mô tả chi tiết.
            image: (Tùy chọn) URL hình ảnh.
            api_key: (Tùy chọn) Override API Key.
        """
        payload = {
            "name": name,
            "price": price,
            "category": category,
            "brand": brand,
            "description": description,
            "image": image
        }
        return web_shop_client.request("POST", "/products", api_key=api_key,
                                       required_scope="products:create", data=payload)

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
        """[ADMIN ONLY] Quản trị viên cập nhật thông tin một sản phẩm.

        Args:
            product_id: Mã ID sản phẩm cần chỉnh sửa.
            name: (Tùy chọn) Tên mới.
            price: (Tùy chọn) Giá mới.
            category: (Tùy chọn) Danh mục mới.
            brand: (Tùy chọn) Thương hiệu mới.
            description: (Tùy chọn) Mô tả mới.
            image: (Tùy chọn) URL hình ảnh mới.
            api_key: (Tùy chọn) Override API Key.
        """
        payload = {}
        if name is not None: payload["name"] = name
        if price is not None: payload["price"] = price
        if category is not None: payload["category"] = category
        if brand is not None: payload["brand"] = brand
        if description is not None: payload["description"] = description
        if image is not None: payload["image"] = image

        return web_shop_client.request("PUT", f"/products/{product_id}", api_key=api_key,
                                       required_scope="products:update", data=payload)

    @mcp.tool()
    def admin_delete_product(product_id: str, api_key: str = None) -> str:
        """[ADMIN ONLY] Quản trị viên xoá một sản phẩm khỏi hệ thống.

        Args:
            product_id: Mã ID sản phẩm cần xoá.
            api_key: (Tùy chọn) Override API Key.
        """
        return web_shop_client.request("DELETE", f"/products/{product_id}", api_key=api_key,
                                       required_scope="products:delete")
