from app import db
from datetime import datetime

class Lesson(db.Model):
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(20))  # 'video', 'document', 'text', 'quiz'
    content_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, nullable=False)
    duration_minutes = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    progress_records = db.relationship('LessonProgress', backref='lesson', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Serialize lesson to dictionary."""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'content_type': self.content_type,
            'content_url': self.content_url,
            'description': self.description,
            'order_index': self.order_index,
            'duration_minutes': self.duration_minutes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        """String representation of Lesson."""
        return f'<Lesson {self.title}>'