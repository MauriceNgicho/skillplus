import pytest
from app.models.user import User


@pytest.mark.auth
class TestRegistration:
    """Test user registration endpoint."""
    
    def test_register_success(self, client, company):
        """Test successful user registration."""
        # Arrange
        data = {
            'company_id': company.id,
            'email': 'newuser@testco.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'employee'
        }
        
        # Act
        response = client.post('/api/auth/register', json=data)
        
        # Assert
        assert response.status_code == 201
        assert 'user' in response.json
        assert response.json['user']['email'] == 'newuser@testco.com'
        assert response.json['user']['role'] == 'employee'
        
        # Verify user exists in database
        user = User.query.filter_by(email='newuser@testco.com').first()
        assert user is not None
        assert user.company_id == company.id
    
    def test_register_duplicate_email(self, client, company, employee_user):
        """Test registration with duplicate email fails."""
        data = {
            'company_id': company.id,
            'email': 'employee@testco.com',  # Already exists
            'password': 'password123',
            'first_name': 'Duplicate',
            'last_name': 'User'
        }
        
        response = client.post('/api/auth/register', json=data)
        
        assert response.status_code == 400
        assert 'error' in response.json
        assert 'already exists' in response.json['error'].lower()
    
    def test_register_missing_required_fields(self, client, company):
        """Test registration with missing fields fails."""
        # Missing email
        data = {
            'company_id': company.id,
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = client.post('/api/auth/register', json=data)
        assert response.status_code == 400
    
    def test_register_weak_password(self, client, company):
        """Test registration with weak password fails."""
        data = {
            'company_id': company.id,
            'email': 'test@testco.com',
            'password': 'weak',  # Less than 8 characters
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = client.post('/api/auth/register', json=data)
        
        assert response.status_code == 400
        assert 'password' in response.json['error'].lower()
    
    def test_register_invalid_company(self, client):
        """Test registration with non-existent company fails."""
        data = {
            'company_id': 99999,
            'email': 'test@test.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = client.post('/api/auth/register', json=data)
        
        assert response.status_code == 404
        assert 'company' in response.json['error'].lower()
    
    def test_register_invalid_role(self, client, company):
        """Test registration with invalid role fails."""
        data = {
            'company_id': company.id,
            'email': 'test@testco.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'superuser'  # Invalid role
        }
        
        response = client.post('/api/auth/register', json=data)
        
        assert response.status_code == 400
        assert 'role' in response.json['error'].lower()


@pytest.mark.auth
class TestLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client, employee_user):
        """Test successful login."""
        data = {
            'email': 'employee@testco.com',
            'password': 'employee123'
        }
        
        response = client.post('/api/auth/login', json=data)
        
        assert response.status_code == 200
        assert 'access_token' in response.json
        assert 'refresh_token' in response.json
        assert 'user' in response.json
        assert response.json['user']['email'] == 'employee@testco.com'
    
    def test_login_invalid_email(self, client):
        """Test login with non-existent email fails."""
        data = {
            'email': 'nonexistent@test.com',
            'password': 'password123'
        }
        
        response = client.post('/api/auth/login', json=data)
        
        assert response.status_code == 401
        assert 'error' in response.json
    
    def test_login_wrong_password(self, client, employee_user):
        """Test login with wrong password fails."""
        data = {
            'email': 'employee@testco.com',
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/auth/login', json=data)
        
        assert response.status_code == 401
    
    def test_login_inactive_user(self, client, inactive_user):
        """Test login with inactive user fails."""
        data = {
            'email': 'inactive@testco.com',
            'password': 'inactive123'
        }
        
        response = client.post('/api/auth/login', json=data)
        
        assert response.status_code == 403
        assert 'inactive' in response.json['error'].lower()
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials fails."""
        response = client.post('/api/auth/login', json={})
        
        assert response.status_code == 400


@pytest.mark.auth
class TestProtectedRoutes:
    """Test JWT authentication on protected routes."""
    
    def test_access_without_token(self, client):
        """Test accessing protected route without token fails."""
        response = client.get('/api/courses')
        
        assert response.status_code == 401
    
    def test_access_with_valid_token(self, client, employee_token):
        """Test accessing protected route with valid token succeeds."""
        headers = {'Authorization': f'Bearer {employee_token}'}
        response = client.get('/api/courses', headers=headers)
        
        assert response.status_code == 200
    
    def test_access_with_invalid_token(self, client):
        """Test accessing protected route with invalid token fails."""
        headers = {'Authorization': 'Bearer invalid_token_here'}
        response = client.get('/api/courses', headers=headers)
        
        assert response.status_code == 422
    
    def test_me_endpoint(self, client, employee_token, employee_user):
        """Test /me endpoint returns current user."""
        headers = {'Authorization': f'Bearer {employee_token}'}
        response = client.get('/api/auth/me', headers=headers)
        
        assert response.status_code == 200
        assert response.json['email'] == 'employee@testco.com'
        assert response.json['role'] == 'employee'


@pytest.mark.auth
class TestTokenRefresh:
    """Test token refresh functionality."""
    
    def test_refresh_token_success(self, client, employee_user):
        """Test refreshing access token with valid refresh token."""
        # First login to get refresh token
        login_response = client.post(
            '/api/auth/login',
            json={'email': 'employee@testco.com', 'password': 'employee123'}
        )
        refresh_token = login_response.json['refresh_token']
        
        # Use refresh token to get new access token
        headers = {'Authorization': f'Bearer {refresh_token}'}
        response = client.post('/api/auth/refresh', headers=headers)
        
        assert response.status_code == 200
        assert 'access_token' in response.json
    
    def test_refresh_with_access_token_fails(self, client, employee_token):
        """Test that access token cannot be used for refresh."""
        headers = {'Authorization': f'Bearer {employee_token}'}
        response = client.post('/api/auth/refresh', headers=headers)
        
        # Should fail because we're using access token not refresh token
        assert response.status_code == 422