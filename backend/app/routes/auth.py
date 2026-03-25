from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity
)
from app import db
from app.models.user import User
from app.models.company import Company
from app.utils.decorators import get_current_user, role_required

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request body:
        {
            "company_id": 1,
            "email": "user@example.com",
            "password": "securepassword",
            "first_name": "John",
            "last_name": "Doe",
            "role": "employee"  # Optional, defaults to 'employee'
        }
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['company_id', 'email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    company_id = data.get('company_id')
    email = data.get('email').lower().strip()
    
    # Validate company exists and is active
    company = Company.query.get(company_id)
    if not company:
        return jsonify({'error': 'Company not found'}), 404
    
    if not company.is_active:
        return jsonify({'error': 'Company is inactive'}), 403
    
    # Check user limit
    current_user_count = User.query.filter_by(company_id=company_id, is_active=True).count()
    if current_user_count >= company.max_users:
        return jsonify({'error': f'Company has reached maximum user limit ({company.max_users})'}), 403
    
    # Check for duplicate email in company
    if User.query.filter_by(company_id=company_id, email=email).first():
        return jsonify({'error': 'User with this email already exists in the company'}), 400
    
    # ✅ Validate password strength
    password = data.get('password')
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long'}), 400
    
    # Validate role
    valid_roles = ['admin', 'manager', 'employee']
    role = data.get('role', 'employee')
    if role not in valid_roles:
        return jsonify({'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'}), 400
    
    # Create user
    user = User(
        company_id=company_id,
        email=email,
        first_name=data.get('first_name').strip(),
        last_name=data.get('last_name').strip(),
        role=role
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'User created successfully',
        'user': user.to_dict(include_company=True)  # Include company info
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT tokens.
    
    Request body:
        {
            "email": "user@example.com",
            "password": "password123"
        }
    """
    data = request.get_json()
    
    # Validate required fields
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    email = data.get('email').lower().strip()
    password = data.get('password')
    
    # Find user by email (across all companies)
    user = User.query.filter_by(email=email).first()
    
    # Generic error message
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Check if user is active
    if not user.is_active:
        return jsonify({'error': 'Account is inactive. Contact your administrator.'}), 403
    
    # Check if company is active
    if not user.company.is_active:
        return jsonify({'error': 'Company account is inactive'}), 403
    
    # ✅ IMPROVEMENT 12: Update last_login timestamp (if you added this field)
    # from datetime import datetime
    # user.last_login = datetime.utcnow()
    # db.session.commit()
    
    # Create tokens
    # NOTE: JWT "sub" must be a string for some JWT backends/versions.
    # We store it as a string and cast back to int when querying the DB.
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(include_company=True)
    }), 200


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token.
    
    Headers:
        Authorization: Bearer <refresh_token>
    """
    current_user_id = get_jwt_identity()
    try:
        current_user_id_int = int(current_user_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid token subject'}), 401
    
    # Validate user still exists and is active
    user = User.query.get(current_user_id_int)
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 401
    
    if not user.company.is_active:
        return jsonify({'error': 'Company account is inactive'}), 403
    
    new_access_token = create_access_token(identity=str(current_user_id_int))
    
    return jsonify({'access_token': new_access_token}), 200


@bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """
    Get current authenticated user's information.
    
    Headers:
        Authorization: Bearer <access_token>
    """
    # Use helper function for consistency
    user = get_current_user()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Include company info
    return jsonify(user.to_dict(include_company=True)), 200


# ✅ IMPROVEMENT 16: Add logout endpoint (optional for JWT, but good practice)
@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user.
    
    Note: With JWT, logout is typically handled client-side by deleting the token.
    This endpoint exists for consistency and can be extended with token blacklisting.
    """
    # For now, just return success
    # In production, you might implement token blacklisting using Redis
    
    return jsonify({'message': 'Logged out successfully'}), 200


# ✅ IMPROVEMENT 17: Add password change endpoint
@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change current user's password.
    
    Request body:
        {
            "current_password": "oldpassword",
            "new_password": "newpassword"
        }
    """
    user = get_current_user()
    data = request.get_json()
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    # Validate required fields
    if not current_password or not new_password:
        return jsonify({'error': 'Current password and new password are required'}), 400
    
    # Verify current password
    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Validate new password
    if len(new_password) < 8:
        return jsonify({'error': 'New password must be at least 8 characters long'}), 400
    
    if current_password == new_password:
        return jsonify({'error': 'New password must be different from current password'}), 400
    
    # Update password
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200


# ✅ IMPROVEMENT 18: Add endpoint to check if email exists (for registration forms)
@bp.route('/check-email', methods=['POST'])
def check_email():
    """
    Check if email already exists in a company.
    
    Useful for frontend validation during registration.
    
    Request body:
        {
            "email": "user@example.com",
            "company_id": 1
        }
    """
    data = request.get_json()
    
    email = data.get('email', '').lower().strip()
    company_id = data.get('company_id')
    
    if not email or not company_id:
        return jsonify({'error': 'Email and company_id are required'}), 400
    
    exists = User.query.filter_by(company_id=company_id, email=email).first() is not None
    
    return jsonify({'exists': exists}), 200