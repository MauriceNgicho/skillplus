from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from app import db
from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.utils.decorators import get_current_user, role_required

bp = Blueprint('enrollments', __name__, url_prefix='/api/enrollments')


@bp.route('', methods=['POST'])
@jwt_required()
def enroll():
    """
    Enroll user(s) in a course.
    self-enrollment (employee):
    {
        "course_id": 1
    }
    Bulk enrollment (admin/manager):
    {
        "course_id": 1,
        "user_ids": [2, 3, 4]
    }
    """
    user = get_current_user()
    data = request.get_json()
    # validate required fields
    if not data or not data.get('course_id'):
        return jsonify({"error": "course_id is required"}), 400
    course_id = data['course_id']
    # Get course and check if it exists
    course = Course.query.get_or_404(course_id)
    #check company isolation
    if course.company_id != user.company_id:
        return jsonify({"error": "Course not found"}), 404
    # Check if course is published
    if not course.is_published:
        return jsonify({"error": "Cannot enroll in unpublished course"}), 400
    # Determine who to enroll
    user_ids_to_enroll = data.get('user_ids', [])
    if user_ids_to_enroll:
        # Bulk enrollment - only admin/manager can do this
        if user.role not in ['admin', 'manager']:
            return jsonify({"error": "Only admins and managers can enroll multiple users"}), 403
        # Validate users exist and belong to the same company
        users_to_enroll = User.query.filter(
            User.id.in_(user_ids_to_enroll),
            User.company_id == user.company_id
            ).all()
        if len(users_to_enroll) != len(user_ids_to_enroll):
            return jsonify({"error": "Some user IDS are invalid"}), 400
    else:
        # Self-enrollement
        users_to_enroll = [user]

    # Enroll users
    enrolled = []
    already_enrolled = []

    for user_to_enroll in users_to_enroll:
        # Check if already enrolled
        existing_enrollment = Enrollment.query.filter_by(
            user_id=user_to_enroll.id,
            course_id=course.id
        ).first()
        if existing_enrollment:
            already_enrolled.append({
                'user_id': user_to_enroll.id,
                'email': user_to_enroll.email
            })
            continue
        
        # Create enrollment
        enrollment = Enrollment(
            user_id=user_to_enroll.id,
            course_id=course.id,
            enrolled_at=datetime.utcnow(),
            status='enrolled'
        )
        db.session.add(enrollment)
        enrolled.append({
            'user_id': user_to_enroll.id,
            'email': user_to_enroll.email
        })
    db.session.commit()
    return jsonify({
        "message": "Enrollment process completed",
        "enrolled": enrolled,
        "already_enrolled": already_enrolled,
        "course": {
            "id": course.id,
            "title": course.title
        }
    }), 201

@bp.route('/my-courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    """
    Get all courses the current user is enrolled in.
     Response:
    [
        {
            "course_id": 1,
            "course_title": "Course 1",
            "enrolled_at": "2024-01-01T12:00:00Z",
            "status": "enrolled"
        },
    Includes progress information for each course.
    """
    user = get_current_user()
    # Get all enrollment with progress for the user
    enrollments = Enrollment.query.filter_by(user_id=user.id).all()
    # Sort by enrolled_at in python.
    enrollments = sorted(enrollments, key=lambda e: e.enrolled_at, reverse=True)
    courses_data = []
    for enrollment in enrollments:
        course_dict = enrollment.to_dict(include_course=True, include_progress=True)
        courses_data.append(course_dict)

    return jsonify({
        'enrollments': courses_data,
        'total_enrolments': len(courses_data)
    }), 200

@bp.route('/<int:enrollment_id>', methods=['DELETE'])
@jwt_required()
def unenroll(enrollment_id):
    """
    Unenroll from a course.
    
    Users can unenroll themselves.
    Admins/managers can unenroll anyone from their company.
    """
    user = get_current_user()
    # Get enrollment
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    # Check company isolation
    if enrollment.course.company_id != user.company_id:
        return jsonify({'error': 'Enrollment not found'}), 404
    # Check authorization
    if enrollment.user_id != user.id and user.role not in ['admin', 'manager']:
        return jsonify({'error': 'You can only unenroll yourself'}), 403
    
    course_title = enrollment.course.title
    user_email = enrollment.user.email
    
    # Delete enrollment (cascade will delete progress records)
    db.session.delete(enrollment)
    db.session.commit()
    
    return jsonify({
        'message': f'Successfully unenrolled {user_email} from "{course_title}"'
    }), 200

@bp.route('/courses/<int:course_id>/students', methods=['GET'])
@jwt_required()
@role_required('admin', 'manager')
def get_course_students(course_id):
    """
    Get all students enrolled in a course.
    
    Only accessible to admin/manager.
    Includes progress information for each student.
    """
    user = get_current_user()
    # Get course
    course = Course.query.get_or_404(course_id)
    # Check company isolation
    if course.company_id != user.company_id:
        return jsonify({'error': 'Course not found'}), 404
    # Get all enrollments
    enrollments = Enrollment.query.filter_by(course_id=course.id).all()
    # Sort by enrolled_at in python.
    enrollments = sorted(enrollments, key=lambda e: e.enrolled_at, reverse=True)
    students = []
    for enrollment in enrollments:
        student_data = {
            'enrollment_id': enrollment.id,
            'user': enrollment.user.to_dict(),
            'enrolled_at': enrollment.enrolled_at.isoformat(),
            'status': enrollment.status
        }
        
        # Calculate progress
        progress_data = enrollment.to_dict(include_progress=True)
        student_data['progress'] = {
            'completed_lessons': progress_data.get('completed_lessons', 0),
            'total_lessons': progress_data.get('total_lessons', 0),
            'progress_percentage': progress_data.get('progress_percentage', 0)
        }
        
        students.append(student_data)
    
    return jsonify({
        'course': {
            'id': course.id,
            'title': course.title
        },
        'students': students,
        'total': len(students)
    }), 200