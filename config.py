import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost:5432/demo'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
# os.environ.get('DATABASE_URL')