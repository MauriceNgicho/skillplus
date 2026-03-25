from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.course import Course
from app.models.lesson import Lesson
from app.utils.decorators import get_current_user, role_required

bp = Blueprint('lessons', __name__, url_prefix='/api')

# Allowed file extensions for uploads
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'csv', 'xls', 'xlsx', 'ppt', 'pptx'}
ALLOWED_EXTENSIONS = ALLOWED_VIDEO_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_content_type_from_extension(filename):
    """Get the content type from the file extension."""
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ALLOWED_VIDEO_EXTENSIONS:
        return 'video'
    elif ext in ALLOWED_DOCUMENT_EXTENSIONS:
        return 'document'
    return 'text'

@bp.route('/courses/<int:course_id>/lessons', methods=['GET'])
@jwt_required()
def get_course_lessons(course_id):
    """
    Get all lessons for a course.
    Return lessons sorted by order_index.
    """
    user = get_current_user()
    course = Course.query.get_or_404(course_id)
    # Check company isolation
    if course.company_id != user.company_id:
        return jsonify({"error": "Course not found"}), 404
    # Employees can only see published lessons
    if not course.is_published and user.role == 'employee':
        return jsonify({"error": "Course not found"}), 404
    # Get lessons
    lessons = course.lessons.order_by(Lesson.order_index).all()
    # Return lessons
    return jsonify({
        'lessons': [lesson.to_dict() for lesson in lessons],
        'total': len(lessons),
        'course': {
            'id': course.id,
            'title': course.title
        }
    }), 200

@bp.route('/courses/<int:course_id>/lessons', methods=['POST'])
@jwt_required()
@role_required('admin', 'manager')
def create_lesson(course_id):
    """
    Create a new lesson for a course.
    Only admin or course creator can create a lesson.
    Request body:
    {
        "title": "Lesson Title",
        "description": "Lesson Description",
        "content_type": "video",
        "content_url": "https://example.com/video.mp4",
        "duration_minutes": 10
    }
    """
    user = get_current_user()
    course = Course.query.get_or_404(course_id)
    # Check company isolation
    if course.company_id != user.company_id:
        return jsonify({"error": "Course not found"}), 404
    # check ownership
    if user.role != 'admin' and course.instructor_id != user.id:
        return jsonify({"error": "You do not have permission to create a lesson for this course"}), 403
    # Validate input
    data = request.get_json()
    # Validate required fields
    if not data or not data.get('title'):
        return jsonify({"error": "Title is required"}), 400
    # Auto-assign order index
    max_order = db.session.query(
        db.func.max(Lesson.order_index)
    ).filter_by(course_id=course_id).scalar()
    next_order = (max_order or 0) + 1
    # Create lesson
    lesson = Lesson(
        course_id=course_id,
        title=data['title'],
        description=data.get('description').strip() or None,
        content_type=data.get('content_type', 'text'),
        content_url=data.get('content_url', '').strip() or None,
        duration_minutes=data.get('duration_minutes', 0),
        order_index=next_order
    )
    db.session.add(lesson)
    db.session.commit()
    return jsonify({
        "message": "Lesson created successfully",
        "lesson": lesson.to_dict()
    }), 201

@bp.route('/lessons/<int:lesson_id>', methods=['GET'])
@jwt_required()
def get_lesson(lesson_id):
    """
    Get a single lesson by ID.
    Accessible if user has access to the parent course.
    Employees can only see published lessons.
    Admins and Managers can see all lessons.
    """
    user = get_current_user()
    lesson = Lesson.query.get_or_404(lesson_id)
    # Check company isolation
    if lesson.course.company_id != user.company_id:
        return jsonify({"error": "Lesson not found"}), 404
    # Employees can only see published lessons
    if not lesson.course.is_published and user.role == 'employee':
        return jsonify({"error": "Lesson not found"}), 404
    # Return lesson
    return jsonify(lesson.to_dict()), 200

@bp.route('/lessons/<int:lesson_id>', methods=['PUT'])
@jwt_required()
@role_required('admin', 'manager')
def update_lesson(lesson_id):
    """
    Update a lesson by ID.
    Only admin or course creator can update a lesson.
    Request body:
    {
        "title": "Lesson Title",
        "description": "Lesson Description",
        "content_type": "video",
        "content_url": "https://example.com/video.mp4",
        "duration_minutes": 10
    }
    """
    user = get_current_user()
    # Get lesson
    lesson = Lesson.query.get_or_404(lesson_id)
    # Check company isolation
    if lesson.course.company_id != user.company_id:
        return jsonify({"error": "Lesson not found"}), 404
    # check ownership
    if user.role != 'admin' and lesson.course.instructor_id != user.id:
        return jsonify({"error": "You do not have permission to update this lesson"}), 403
    # Validate input
    data = request.get_json() or {}
    # Update fields (allow clearing by sending None/empty)
    if 'title' in data:
        if not data['title'] or not data['title'].strip():
            return jsonify({"error": "Title cannot be empty"}), 400
        lesson.title = data['title'].strip()
    if 'description' in data:
        lesson.description = data.get('description', '').strip() or None
    if 'content_type' in data:
        lesson.content_type = data.get('content_type', 'text').strip()
    if 'content_url' in data:
        lesson.content_url = data.get('content_url', '').strip() or None
    if 'duration_minutes' in data:
        duration = data.get('duration_minutes')
        if duration is not None and not isinstance(duration, int) or duration < 0:
            return jsonify({"error": "Duration must be a positive integer"}), 400
        lesson.duration_minutes = duration
    # Commit changes
    db.session.commit()
    return jsonify({
        "message": "Lesson updated successfully",
        "lesson": lesson.to_dict()
    }), 200

@bp.route('/lessons/<int:lesson_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin', 'manager')
def delete_lesson(lesson_id):
    """
    Delete a lesson.
    
    Only course creator or admin can delete.
    Automatically adjusts order_index of remaining lessons.
    """
    user = get_current_user()
    # Get lesson
    lesson = Lesson.query.get_or_404(lesson_id)
    # Check company isolation
    if lesson.course.company_id != user.company_id:
        return jsonify({'error': 'Lesson not found'}), 404
    # Check ownership
    if user.role != 'admin' and lesson.course.instructor_id != user.id:
        return jsonify({'error': 'Only the course creator can delete lessons'}), 403
    
    course_id = lesson.course_id
    deleted_order = lesson.order_index
    lesson_title = lesson.title
    
    # Delete lesson (cascade will delete progress records)
    db.session.delete(lesson)
    db.session.flush()  # Flush to get the deletion registered
    # Reorder remaining lessons
    remaining_lessons = (
        Lesson.query
        .filter_by(course_id=course_id)
        .filter(Lesson.order_index > deleted_order)
        .order_by(Lesson.order_index)
        .all()
    )
    
    for lesson in remaining_lessons:
        lesson.order_index -= 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'Lesson "{lesson_title}" deleted successfully',
        'reordered_count': len(remaining_lessons)
    }), 200

@bp.route('/lessons/<int:lesson_id>/upload', methods=['POST'])
@jwt_required()
@role_required('admin', 'manager')
def upload_lesson_content(lesson_id):
    """
    Upload content file for a lesson (video or document).
    
    Only course creator or admin can upload.
    
    Form data:
        file: The file to upload
    """
    user = get_current_user()
    # Get lesson
    lesson = Lesson.query.get_or_404(lesson_id)
    # Check company isolation
    if lesson.course.company_id != user.company_id:
        return jsonify({'error': 'Lesson not found'}), 404
    # Check ownership
    if user.role != 'admin' and lesson.course.instructor_id != user.id:
        return jsonify({'error': 'Only the course creator can upload content'}), 403
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    # Secure the filename
    filename = secure_filename(file.filename)
    # Create course-specific directory
    upload_dir = os.path.join('uploads', 'courses', str(lesson.course_id))
    os.makedirs(upload_dir, exist_ok=True)
    # Add timestamp to filename to avoid conflicts
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{timestamp}{ext}"
    # Full path
    filepath = os.path.join(upload_dir, unique_filename)
    # Save file
    file.save(filepath)
    # Update lesson with file path and auto-detect content type
    lesson.content_url = f'/{filepath}'  # Store as /uploads/courses/1/file.mp4
    lesson.content_type = get_content_type_from_extension(filename)
    
    db.session.commit()
    return jsonify({
        'message': 'File uploaded successfully',
        'lesson': lesson.to_dict(),
        'file': {
            'filename': unique_filename,
            'path': lesson.content_url,
            'type': lesson.content_type
        }
    }), 200

@bp.route('/lessons/<int:lesson_id>/reorder', methods=['PUT'])
@jwt_required()
@role_required('admin', 'manager')
def reorder_lesson(lesson_id):
    """
    Change the order of a lesson.
    
    Request body:
        {
            "new_order": 3  // New position (1-based index)
        }
    
    This will shift other lessons accordingly.
    """
    user = get_current_user()
    # Get lesson
    lesson = Lesson.query.get_or_404(lesson_id)
    # Check company isolation
    if lesson.course.company_id != user.company_id:
        return jsonify({'error': 'Lesson not found'}), 404
    # Check ownership
    if user.role != 'admin' and lesson.course.instructor_id != user.id:
        return jsonify({'error': 'Only the course creator can reorder lessons'}), 403
    data = request.get_json()
    new_order = data.get('new_order')
    if not new_order or not isinstance(new_order, int) or new_order < 1:
        return jsonify({'error': 'new_order must be a positive integer'}), 400
    old_order = lesson.order_index
    # Get total lessons in course
    total_lessons = Lesson.query.filter_by(course_id=lesson.course_id).count()
    if new_order > total_lessons:
        return jsonify({'error': f'new_order cannot exceed total lessons ({total_lessons})'}), 400
    if new_order == old_order:
        return jsonify({'message': 'Lesson is already at this position', 'lesson': lesson.to_dict()}), 200

    # Reorder logic
    if new_order < old_order:
        # Moving up (decreasing order_index)
        # Shift lessons down that are between new_order and old_order
        lessons_to_shift = (
            Lesson.query.filter_by(course_id=lesson.course_id)
            .filter(Lesson.order_index >= new_order)
            .filter(Lesson.order_index < old_order)
            .all()
            )
        for l in lessons_to_shift:
            l.order_index += 1
    else:
        # Moving down (increasing order_index)
        # Shift lessons up that are between old_order and new_order
        lessons_to_shift = (
            Lesson.query.filter_by(course_id=lesson.course_id)\
            .filter(Lesson.order_index > old_order)\
            .filter(Lesson.order_index <= new_order)\
            .all()
            )
        for l in lessons_to_shift:
            l.order_index -= 1
    
    # Update the lesson's order
    lesson.order_index = new_order
    
    db.session.commit()
    
    return jsonify({
        'message': f'Lesson moved from position {old_order} to {new_order}',
        'lesson': lesson.to_dict(),
        'shifted_count': len(lessons_to_shift)
    }), 200

@bp.route('/lessons/<int:lesson_id>/content', methods=['GET'])
@jwt_required()
def get_lesson_content(lesson_id):
    """
    Stream lesson content file with authentication.
    Only accessible if user has access to the course.
    """
    user = get_current_user()
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Check company isolation
    if lesson.course.company_id != user.company_id:
        return jsonify({'error': 'Lesson not found'}), 404
    
    # Employees can only access published course content
    if not lesson.course.is_published and user.role == 'employee':
        return jsonify({'error': 'Lesson not found'}), 404
    
    # Check if content exists
    if not lesson.content_url:
        return jsonify({'error': 'No content available for this lesson'}), 404
    
    # Get file path (remove leading /)
    file_path = lesson.content_url.lstrip('/')
    full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', file_path)
    
    if not os.path.exists(full_path):
        return jsonify({'error': 'Content file not found'}), 404
    
    # Get file directory and filename
    directory = os.path.dirname(full_path)
    filename = os.path.basename(full_path)
    
    # Serve file
    from flask import send_from_directory
    return send_from_directory(directory, filename)