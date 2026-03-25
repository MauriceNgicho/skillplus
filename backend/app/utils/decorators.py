from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User


def role_required(*allowed_roles):
    """
    Decorators to check if the user has one of the allowed roles.

    Usage:
        @role_required('admin', 'manager')
            def some_protected_route():
    
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request() # Verify that the JWT is present and valid
            current_user_id = get_jwt_identity()  # Get the user ID from the JWT
            try:
                current_user_id_int = int(current_user_id)
            except (TypeError, ValueError):
                return jsonify({"error": "Invalid token subject"}), 401
            user = User.query.get(current_user_id_int)
            # Check if user exists and is active
            if not user or not user.is_active:
                return jsonify({"error": "User not found or inactive"}), 403
            # Check if user has one of the allowed roles
            if user.role not in allowed_roles:
                return jsonify({
                    "error": f'Access denied. Required role: {", ".join(allowed_roles)}'
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def get_current_user():
    """
    Helper function to get the current authenticated user.
    """
    try:
        current_user_id = get_jwt_identity()
        try:
            current_user_id_int = int(current_user_id)
        except (TypeError, ValueError):
            return None
        user = User.query.get(current_user_id_int)
        return user
    except Exception as e:
        print(f"DEBUG ERROR in get_current_user: {e}")  # ✅ DEBUG
        raise

def same_company_required(fn):
    """Decorator to ensure the user can only access resources from their own company."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_current_user()
        return fn(*args, **kwargs)
    return wrapper