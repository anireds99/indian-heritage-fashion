"""
Controllers package for handling HTTP requests.
"""
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.admin_controller import admin_bp

__all__ = ['auth_bp', 'user_bp', 'admin_bp']
