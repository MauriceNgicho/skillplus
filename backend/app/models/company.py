from app import db
from datetime import datetime


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    subdomain = db.Column(db.String(50), nullable=False, unique=True)
    subscription_plan = db.Column(db.String(20), default='basic')
    max_users = db.Column(db.Integer, default=20)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert company object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'subdomain': self.subdomain,
            'subscription_plan': self.subscription_plan,
            'max_users': self.max_users,
            'is_active': self.is_active,
            'user_count': len(self.users) if self.users else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        """String representation of the Company."""
        return f'<Company {self.name}>'