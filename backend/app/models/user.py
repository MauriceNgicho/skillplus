from app import db, bcrypt
from datetime import datetime
from sqlalchemy import Enum


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = ( db.UniqueConstraint('company_id','email', name='uq_company_email'), ) # Ensure email is unique within the same company

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(
        Enum('admin', 'manager', 'employee', name='user_roles'),
        nullable=False, default='employee'
        )
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = db.relationship('Company', backref='users')
    enrollments = db.relationship('Enrollment', backref='user', lazy='selectin', cascade="all, delete-orphan")

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Returns the user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def has_role(self, *roles):
        """Check if the user has one of the specified roles."""
        return self.role in roles
    
    def to_dict(self, include_company=False):
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'company_id': self.company_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_company and self.company:
            data['company'] = self.company.to_dict()
        
        return data
    
    def __repr__(self):
        """String representation of the User."""
        return f"<User {self.email} ({self.role})>"