import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://localhost/skillplus')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    UPLOAD_FOLDER = 'uploads/'       
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    JWT_ERROR_MESSAGE_KEY = 'error'  # Use 'error' key for JWT error messages
    JWT_IDENTITY_CLAIM = 'sub'  # Use 'sub' claim for user identity in JWT
    JWT_DECODE_ALGORITHMS = ['HS256']  # Specify the algorithm for decoding JWTs

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'postgresql://localhost/skillplus_test')
    WTF_CSRF_ENABLED = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)