from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.course import Course
from app.models.lesson import Lesson
from app.utils.decorators import role_required, get_current_user

bp = Blueprint('courses', __name__, url_prefix='/api/courses')


@bp.route('', methods=['GET'])
@jwt_required()
def get_courses():
    """
    Get all courses for the user's company.
    Employees can only see published courses. Admins and Managers can see all courses.
    """
    user = get_current_user()
    query = Course.query.filter_by(company_id=user.company_id)
    
    # Employees can ONLY see published courses (ignore query params)
    if user.role == 'employee':
        query = query.filter_by(is_published=True)
    else:
        # Managers/Admins can filter by published status
        is_published = request.args.get('is_published')
        if is_published is not None:
            is_published_bool = is_published.lower() in ['true', '1', 'yes']
            query = query.filter_by(is_published=is_published_bool)
    
    courses = query.order_by(Course.created_at.desc()).all()
    
    return jsonify({
        'courses': [course.to_dict(include_stats=True) for course in courses],
        'total': len(courses)
    }), 200

@bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    """
    Get a sinlge course by ID with all lessons.
    
    Only accessible if:
    - The course belongs to the user's company
    - The course is published OR the user is an admin/manager
    """
    user = get_current_user()
    # Get course
    course = Course.query.get_or_404(course_id)
    # Check company isolation
    if course.company_id != user.company_id:
        return jsonify({"error": "Course not found"}), 404
    # Check if course is published or user has elevated role
    if not course.is_published and user.role == 'employee':
        return jsonify({"error": "Course not found"}), 404
    # Return course with lessons
    return jsonify(course.to_dict(include_lessons=True, include_stats=True)), 200

@bp.route('', methods=['POST'])
@jwt_required()
@role_required('admin', 'manager')
def create_course():
    """
    Create a new course(admin and manager only).
    Request body:
    {
        "title": "Course Title",
        "description": "Course Description",
        "is_published": false
    }
    """
    user = get_current_user()
    data = request.get_json()
    # Validate input
    if not data or not data.get('title'):
        return jsonify({"error": "Title is required"}), 400
    # Create course
    course = Course(
        company_id=user.company_id,  # Ensure course is created under the user's company
        instructor_id=user.id,  # Creator is the instructor
        title=data['title'],
        description=data.get('description'),
        thumbnail_url=data.get('thumbnail_url'),
        is_published=data.get('is_published', False) # Default to draft if not provided
    )
    db.session.add(course)
    db.session.commit()
    return jsonify({
        "message": "Course created successfully",
        "course": course.to_dict()
    }), 201

@bp.route('/<int:course_id>', methods=['PUT'])
@jwt_required()
@role_required('admin', 'manager')
def update_course(course_id):
    """
    Update an existing course (admin and manager only).
    """
    user = get_current_user()
    course = Course.query.get_or_404(course_id)
    
    # Check company isolation
    if course.company_id != user.company_id:
        return jsonify({"error": "Course not found"}), 404
    
    # Check ownership
    if user.role != 'admin' and course.instructor_id != user.id:
        return jsonify({"error": "You do not have permission to update this course"}), 403
    
    data = request.get_json() or {}
    
    # Update fields (allow clearing by sending None/empty)
    if 'title' in data:
        if not data['title'] or not data['title'].strip():
            return jsonify({"error": "Title cannot be empty"}), 400
        course.title = data['title'].strip()
    
    if 'description' in data:
        course.description = data.get('description', '').strip() or None
    
    if 'thumbnail_url' in data:
        course.thumbnail_url = data.get('thumbnail_url', '').strip() or None
    
    if 'is_published' in data:
        is_pub = data.get('is_published')
        if not isinstance(is_pub, bool):
            return jsonify({'error': 'is_published must be a boolean'}), 400
        course.is_published = is_pub
    
    db.session.commit()
    
    return jsonify({
        "message": "Course updated successfully",
        "course": course.to_dict()
    }), 200


@bp.route('/<int:course_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin', 'manager')
def delete_course(course_id):
    """
    Delete a course (admin or course creators).
    Also deletes all associated lessons and enrollments(cascading delete).
    """
    user = get_current_user()
    course = Course.query.get_or_404(course_id)
    # Check company isolation
    if course.company_id != user.company_id:
        return jsonify({"error": "Course not found"}), 404
    # Check ownership(only creator or admin can delete)
    if user.role != 'admin' and course.instructor_id != user.id:
        return jsonify({"error": "You do not have permission to delete this course"}), 403
    # Check if course has enrollments
    enrollment_count = course.enrollments.count()
    if enrollment_count > 0:
        return jsonify({
            "error": f"Cannot delete course with enrollments. Unpublish it instead"
        }), 400
    # Delete courses
    course_title = course.title
    db.session.delete(course)
    db.session.commit()
    return jsonify({
        "message": f'Course "{course_title}" deleted successfully'
    }), 200

@bp.route('/<int:course_id>/publish', methods=['POST'])
@jwt_required()
@role_required('admin', 'manager')
def publish_course(course_id):
    """
    Publish a course(make it available for enrollment).
    """
    user = get_current_user()
    course = Course.query.get_or_404(course_id)
    # Check company isolation and ownership
    if course.company_id != user.company_id:
        return jsonify({'error': 'course not found'}), 404
    if user.role != 'admin' and course.instructor_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    # Check if course has lessons
    if course.lessons.count() == 0:
        return jsonify({'error': 'Cannot publish course without lessons'}), 400
    # Publish
    course.is_published = True
    db.session.commit()
    return jsonify({
        'message': 'Course published successfully',
        'course': course.to_dict()
    }), 200

@bp.route('/<int:course_id>/unpublish', methods=['POST'])
@jwt_required()
@role_required('admin', 'manager')
def unpublish_course(course_id):
    """
    Unpublish a course(hide from employees).
    Existing enrollment remain, but no new enrollments allowed.
    """
    user = get_current_user()
    course = Course.query.get_or_404(course_id)
    # Check company isolation and ownership
    if course.company_id != user.company_id:
        return jsonify({'error': 'Course not found'}), 404
    if user.role != 'admin' and course.instructor_id != user.id:
        return jsonify({'error': 'You do not have permission to unpublish this course'}), 403
    # Unpublish
    course.is_published = False
    db.session.commit()

    return jsonify({
        'message': 'Course unpublished successfully',
        'course': course.to_dict()
    }), 200