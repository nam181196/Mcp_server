import os
from config.web_shop_config import get_token_for_api_key

def get_webshop_token(user_identifier: str, role: str) -> str:
    """
    Ánh xạ từ thông tin tài khoản OAuth/API Key sang Access Token/Session Cookie của WebShop Backend.
    """
    # Nếu user_identifier là API Key giả lập
    token_info = get_token_for_api_key(user_identifier)
    if token_info:
        return token_info.get("access_token")
    
    # Ánh xạ theo Role từ OAuth (Clerk)
    if role == "admin":
        return os.environ.get("WEB_SHOP_ADMIN_TOKEN", "sk_admin_130f18fa2ddf0b6fbab3e141406b7313")
    return os.environ.get("WEB_SHOP_USER_TOKEN", "sk_user_0468d3872545a0d3a32accf26de87463")
