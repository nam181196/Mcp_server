from config.auth_config import DEFAULT_SCOPES

ROLE_SCOPES = DEFAULT_SCOPES

def get_scopes_for_role(role: str) -> list:
    """Lấy danh sách các scope được phép cho role tương ứng."""
    return ROLE_SCOPES.get(role, ROLE_SCOPES["user"])

def has_required_scope(user_scopes: list, required_scope: str) -> bool:
    """Kiểm tra user có chứa scope yêu cầu không."""
    return required_scope in user_scopes
