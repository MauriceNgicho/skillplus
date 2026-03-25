from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(f'app.config.{config_name.capitalize()}Config')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app, resources={
        r"/api/*": {"origins": "*"},
        r"/uploads/*": {"origins": "*"} # Allow external access to uploaded content for testing.
    })

    @jwt.user_identity_loader
    def user_identity_lookup(user_id):
        """Convert user_id to the format stored in JWT"""
        # Store subject as string to satisfy JWT "sub" requirements.
        return str(user_id)
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Load user from JWT data"""
        # Import here to avoid circular imports during app initialization
        from app.models.user import User
        identity = jwt_data.get("sub")
        try:
            identity_int = int(identity)
        except (TypeError, ValueError):
            return None
        return User.query.get(identity_int)
    # Register blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.courses import bp as courses_bp
    from app.routes.lessons import bp as lessons_bp
    from app.routes.enrollments import bp as enrollments_bp
    from app.routes.progress import bp as progress_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(lessons_bp)
    app.register_blueprint(enrollments_bp)
    app.register_blueprint(progress_bp)

    # Import models to register them with SQLAlchemy
    with app.app_context():
        from app.models import User, Company, Course, Enrollment, Lesson, LessonProgress

    return app
