from app import db
from datetime import datetime

class LessonProgress(db.Model):
    __tablename__ = 'lesson_progress'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'lesson_id', name='uq_user_lesson'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='lesson_progress')
    
    def to_dict(self):
        """Serialize lesson progress to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
    
    def __repr__(self):
        """String representation of LessonProgress."""
        return f'<LessonProgress User:{self.user_id} Lesson:{self.lesson_id} Completed:{self.completed}>'
