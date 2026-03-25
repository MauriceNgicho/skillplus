from app import db
from datetime import datetime

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', name='uq_user_course'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default='enrolled')  # 'enrolled', 'in_progress', 'completed', 'dropped'
    
    def to_dict(self, include_course=False, include_progress=False):
        """Serialize enrollment to dictionary."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'status': self.status,
        }
        
        if include_course:
            data['course'] = self.course.to_dict()
        
        if include_progress:
            # Calculate progress percentage
            total_lessons = self.course.lessons.count()
            if total_lessons > 0:
                from app.models.lesson_progress import LessonProgress
                from app.models.lesson import Lesson
                completed_lessons = LessonProgress.query.filter_by(
                    user_id=self.user_id,
                    completed=True
                ).join(Lesson).filter(Lesson.course_id == self.course_id).count()
                data['progress_percentage'] = round((completed_lessons / total_lessons) * 100, 2)
                data['completed_lessons'] = completed_lessons
                data['total_lessons'] = total_lessons
            else:
                data['progress_percentage'] = 0
                data['completed_lessons'] = 0
                data['total_lessons'] = 0
        
        return data
    
    def __repr__(self):
        """String representation of Enrollment."""
        return f'<Enrollment User:{self.user_id} Course:{self.course_id}>'