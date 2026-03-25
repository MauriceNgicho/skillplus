import pytest
from app import create_app, db
from app.models.company import Company
from app.models.user import User
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment
from app.models.lesson_progress import LessonProgress


@pytest.fixture(scope='function')
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    with app.app_context():
        # Create all tables
        db.create_all()
        yield app
        
        # Cleanup after test
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def company(app):
    """Create a test company."""
    company = Company(
        name='Test Company',
        subdomain='testco',
        subscription_plan='pro',
        max_users=100,
        is_active=True
    )
    db.session.add(company)
    db.session.commit()
    return company


@pytest.fixture(scope='function')
def another_company(app):
    """Create a second company for isolation testing."""
    company = Company(
        name='Another Company',
        subdomain='anotherco',
        subscription_plan='basic',
        max_users=50,
        is_active=True
    )
    db.session.add(company)
    db.session.commit()
    return company


@pytest.fixture(scope='function')
def admin_user(app, company):
    """Create an admin user."""
    user = User(
        company_id=company.id,
        email='admin@testco.com',
        first_name='Admin',
        last_name='User',
        role='admin',
        is_active=True
    )
    user.set_password('admin123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def manager_user(app, company):
    """Create a manager user."""
    user = User(
        company_id=company.id,
        email='manager@testco.com',
        first_name='Manager',
        last_name='User',
        role='manager',
        is_active=True
    )
    user.set_password('manager123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def employee_user(app, company):
    """Create an employee user."""
    user = User(
        company_id=company.id,
        email='employee@testco.com',
        first_name='Employee',
        last_name='User',
        role='employee',
        is_active=True
    )
    user.set_password('employee123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def inactive_user(app, company):
    """Create an inactive user."""
    user = User(
        company_id=company.id,
        email='inactive@testco.com',
        first_name='Inactive',
        last_name='User',
        role='employee',
        is_active=False
    )
    user.set_password('inactive123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def other_company_user(app, another_company):
    """Create user from different company."""
    user = User(
        company_id=another_company.id,
        email='user@anotherco.com',
        first_name='Other',
        last_name='User',
        role='employee',
        is_active=True
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def published_course(app, company, manager_user):
    """Create a published course with lessons."""
    course = Course(
        company_id=company.id,
        instructor_id=manager_user.id,
        title='Python Basics',
        description='Learn Python programming',
        is_published=True
    )
    db.session.add(course)
    db.session.commit()
    
    # Add lessons
    lesson1 = Lesson(
        course_id=course.id,
        title='Introduction',
        content_type='video',
        order_index=1,
        duration_minutes=15
    )
    lesson2 = Lesson(
        course_id=course.id,
        title='Variables',
        content_type='video',
        order_index=2,
        duration_minutes=20
    )
    db.session.add_all([lesson1, lesson2])
    db.session.commit()
    
    return course


@pytest.fixture(scope='function')
def draft_course(app, company, manager_user):
    """Create an unpublished course."""
    course = Course(
        company_id=company.id,
        instructor_id=manager_user.id,
        title='Advanced Python',
        description='Advanced topics',
        is_published=False
    )
    db.session.add(course)
    db.session.commit()
    return course


def get_auth_token(client, email, password):
    """Helper function to get auth token."""
    response = client.post(
        '/api/auth/login',
        json={'email': email, 'password': password}
    )
    if response.status_code == 200:
        return response.json['access_token']
    return None


@pytest.fixture(scope='function')
def admin_token(client, admin_user):
    """Get auth token for admin user."""
    return get_auth_token(client, 'admin@testco.com', 'admin123')


@pytest.fixture(scope='function')
def manager_token(client, manager_user):
    """Get auth token for manager user."""
    return get_auth_token(client, 'manager@testco.com', 'manager123')


@pytest.fixture(scope='function')
def employee_token(client, employee_user):
    """Get auth token for employee user."""
    return get_auth_token(client, 'employee@testco.com', 'employee123')


@pytest.fixture(scope='function')
def auth_headers(admin_token):
    """Get authorization headers with admin token."""
    return {'Authorization': f'Bearer {admin_token}'}