from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from app import db
from app.models.lesson import Lesson
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.lesson_progress import LessonProgress
from app.utils.decorators import get_current_user, role_required

bp = Blueprint('progress', __name__, url_prefix='/api/progress')


@bp.route('/lessons/<int:lesson_id>/complete', methods=['POST'])
@jwt_required()
def mark_lesson_complete(lesson_id):
    """
    Mark a lesson as complete.
    
    User must be enrolled in the course to mark lessons complete.
    """
    user = get_current_user()
    # Get lesson
    lesson = Lesson.query.get_or_404(lesson_id)
    # Check company isolation
    if lesson.course.company_id != user.company_id:
        return jsonify({'error': 'Lesson not found'}), 404
    # Check if user is enrolled in the course
    enrollment = Enrollment.query.filter_by(
        user_id=user.id,
        course_id=lesson.course_id
    ).first() 
    if not enrollment:
        return jsonify({'error': 'You must be enrolled in this course to mark lessons complete'}), 403
    
    # Get or create progress record
    progress = LessonProgress.query.filter_by(
        user_id=user.id,
        lesson_id=lesson_id
    ).first()
    if not progress:
        progress = LessonProgress(
            user_id=user.id,
            lesson_id=lesson_id,
            completed=True,
            completed_at=datetime.utcnow()
        )
        db.session.add(progress)
    else:
        # Update existing record
        if progress.completed:
            return jsonify({
                'message': 'Lesson already marked as complete',
                'progress': progress.to_dict()
            }), 200
        
        progress.completed = True
        progress.completed_at = datetime.utcnow()
    
    # Update enrollment status
    if enrollment.status == 'enrolled':
        enrollment.status = 'in_progress'
    
    db.session.commit()
    
    # Calculate updated course progress
    total_lessons = lesson.course.lessons.count()
    completed_lessons = LessonProgress.query.filter_by(
        user_id=user.id,
        completed=True
    ).join(Lesson).filter(Lesson.course_id == lesson.course_id).count()
    
    progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    # Check if course is now complete
    if completed_lessons == total_lessons:
        enrollment.status = 'completed'
        db.session.commit()
    
    return jsonify({
        'message': 'Lesson marked as complete',
        'progress': progress.to_dict(),
        'course_progress': {
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
            'progress_percentage': round(progress_percentage, 2),
            'course_status': enrollment.status
        }
    }), 200


@bp.route('/lessons/<int:lesson_id>/incomplete', methods=['POST'])
@jwt_required()
def mark_lesson_incomplete(lesson_id):
    """
    Mark a lesson as incomplete (undo completion).
    
    Useful if user clicked complete by mistake.
    """
    user = get_current_user()
    
    # Get lesson
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Check company isolation
    if lesson.course.company_id != user.company_id:
        return jsonify({'error': 'Lesson not found'}), 404
    
    # Get progress record
    progress = LessonProgress.query.filter_by(
        user_id=user.id,
        lesson_id=lesson_id
    ).first()
    
    if not progress or not progress.completed:
        return jsonify({'error': 'Lesson is not marked as complete'}), 400
    
    # Mark as incomplete
    progress.completed = False
    progress.completed_at = None
    
    # Update enrollment status (move from completed back to in_progress)
    enrollment = Enrollment.query.filter_by(
        user_id=user.id,
        course_id=lesson.course_id
    ).first()
    
    if enrollment and enrollment.status == 'completed':
        enrollment.status = 'in_progress'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Lesson marked as incomplete',
        'progress': progress.to_dict()
    }), 200


@bp.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course_progress(course_id):
    """
    Get user's progress for a specific course.
    
    Shows all lessons with completion status.
    """
    user = get_current_user()
    
    # Get course
    course = Course.query.get_or_404(course_id)
    
    # Check company isolation
    if course.company_id != user.company_id:
        return jsonify({'error': 'Course not found'}), 404
    
    # Check enrollment
    enrollment = Enrollment.query.filter_by(
        user_id=user.id,
        course_id=course_id
    ).first()
    
    if not enrollment:
        return jsonify({'error': 'You are not enrolled in this course'}), 403
    
    # Get all lessons
    lessons = course.lessons.order_by(Lesson.order_index).all()
    
    # Get user's progress for all lessons
    progress_records = LessonProgress.query.filter_by(user_id=user.id).filter(
        LessonProgress.lesson_id.in_([l.id for l in lessons])
    ).all()
    
    progress_dict = {p.lesson_id: p for p in progress_records}
    
    # Build lessons with progress
    lessons_with_progress = []
    for lesson in lessons:
        lesson_data = lesson.to_dict()
        progress = progress_dict.get(lesson.id)
        
        lesson_data['completed'] = progress.completed if progress else False
        lesson_data['completed_at'] = progress.completed_at.isoformat() if progress and progress.completed_at else None
        
        lessons_with_progress.append(lesson_data)
    
    # Calculate overall progress
    total_lessons = len(lessons)
    completed_lessons = sum(1 for l in lessons_with_progress if l['completed'])
    progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    return jsonify({
        'course': {
            'id': course.id,
            'title': course.title,
            'description': course.description
        },
        'enrollment': {
            'enrolled_at': enrollment.enrolled_at.isoformat(),
            'status': enrollment.status
        },
        'progress': {
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percentage': round(progress_percentage, 2)
        },
        'lessons': lessons_with_progress
    }), 200


@bp.route('/my-progress', methods=['GET'])
@jwt_required()
def get_my_progress():
    """
    Get user's progress across all enrolled courses.
    
    Returns summary statistics.
    """
    user = get_current_user()
    
    # Get all enrollments
    enrollments = Enrollment.query.filter_by(user_id=user.id).all()
    
    courses_progress = []
    total_courses = len(enrollments)
    completed_courses = 0
    in_progress_courses = 0
    not_started_courses = 0
    
    for enrollment in enrollments:
        course = enrollment.course
        total_lessons = course.lessons.count()
        
        if total_lessons == 0:
            progress_percentage = 0
            completed_lessons = 0
        else:
            completed_lessons = LessonProgress.query.filter_by(
                user_id=user.id,
                completed=True
            ).join(Lesson).filter(Lesson.course_id == course.id).count()
            
            progress_percentage = (completed_lessons / total_lessons * 100)
        
        # Categorize course
        if completed_lessons == total_lessons and total_lessons > 0:
            completed_courses += 1
            status = 'completed'
        elif completed_lessons > 0:
            in_progress_courses += 1
            status = 'in_progress'
        else:
            not_started_courses += 1
            status = 'not_started'
        
        courses_progress.append({
            'course': {
                'id': course.id,
                'title': course.title,
                'thumbnail_url': course.thumbnail_url
            },
            'enrolled_at': enrollment.enrolled_at.isoformat(),
            'status': status,
            'progress': {
                'completed_lessons': completed_lessons,
                'total_lessons': total_lessons,
                'progress_percentage': round(progress_percentage, 2)
            }
        })
    
    return jsonify({
        'summary': {
            'total_courses': total_courses,
            'completed_courses': completed_courses,
            'in_progress_courses': in_progress_courses,
            'not_started_courses': not_started_courses
        },
        'courses': courses_progress
    }), 200