from app import db
from datetime import datetime

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    thumbnail_url = db.Column(db.String(500))
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', backref='courses')
    instructor = db.relationship('User', foreign_keys=[instructor_id], backref='courses_taught')
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic', cascade='all, delete-orphan', order_by='Lesson.order_index')
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_lessons=False, include_stats=False):
        """Serialize course to dictionary."""
        data = {
            'id': self.id,
            'company_id': self.company_id,
            'title': self.title,
            'description': self.description,
            'thumbnail_url': self.thumbnail_url,
            'instructor_id': self.instructor_id,
            'instructor_name': self.instructor.full_name if self.instructor else None,
            'is_published': self.is_published,
            'lesson_count': self.lessons.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_lessons:
            data['lessons'] = [lesson.to_dict() for lesson in self.lessons]
        
        if include_stats:
            data['enrollment_count'] = self.enrollments.count()
        
        return data
    
    def __repr__(self):
        """String representation of Course."""
        return f'<Course {self.title}>'