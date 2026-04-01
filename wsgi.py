"""
WSGI entry point for production deployment
Use with Gunicorn: gunicorn wsgi:app
"""
import os
from app import app, db

if __name__ == "__main__":
    # Initialize database on first run
    with app.app_context():
        db.create_all()
    app.run()
