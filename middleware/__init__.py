"""
Middleware decorators for authentication and authorization.
Implements decorator pattern for route protection.
"""
from functools import wraps
from flask import session, redirect, url_for, flash, request


def login_required(f):
    """Decorator to require user login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def super_admin_required(f):
    """Decorator to require super admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.admin_login'))
        
        from repositories import AdminRepository
        admin = AdminRepository.find_by_id(session['admin_id'])
        
        if not admin or not admin.is_super_admin():
            flash('Super admin access required.', 'danger')
            return redirect(url_for('admin.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def guest_only(f):
    """Decorator to restrict access to guests only (logged out users)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            return redirect(url_for('user.dashboard'))
        if 'admin_id' in session:
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
