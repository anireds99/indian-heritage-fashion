"""
Authentication controller for handling login, registration, and logout.
Implements Controller pattern following SOLID principles.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services import AuthenticationService
from middleware import guest_only

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_service = AuthenticationService()


@auth_bp.route('/register', methods=['GET', 'POST'])
@guest_only
def register():
    """User registration page and handler."""
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
        
        # Register user
        result = auth_service.register_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(result['message'], 'danger')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
@guest_only
def login():
    """User login page and handler."""
    if request.method == 'POST':
        identifier = request.form.get('identifier')  # email or username
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        # Debug logging
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        logger.info(f"Login attempt for identifier: {identifier}")
        
        result = auth_service.login_user(identifier, password)
        
        logger.info(f"Login result: {result['success']}, Message: {result['message']}")
        
        if result['success']:
            session['user_id'] = result['user'].id
            session['username'] = result['user'].username
            session.permanent = bool(remember)
            
            flash(f"Welcome back, {result['user'].username}!", 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page or url_for('user.dashboard'))
        else:
            flash(result['message'], 'danger')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')


@auth_bp.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    """Admin registration page (restricted - requires special token or super admin)."""
    # In production, add token verification or super admin check
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'admin')
        
        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/admin_register.html')
        
        # Register admin
        result = auth_service.register_admin(
            email=email,
            username=username,
            password=password,
            full_name=full_name,
            role=role
        )
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('auth.admin_login'))
        else:
            flash(result['message'], 'danger')
            return render_template('auth/admin_register.html')
    
    return render_template('auth/admin_register.html')


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page and handler."""
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        identifier = request.form.get('identifier')  # email or username
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        result = auth_service.login_admin(identifier, password)
        
        if result['success']:
            session['admin_id'] = result['admin'].id
            session['admin_username'] = result['admin'].username
            session['admin_role'] = result['admin'].role
            session.permanent = bool(remember)
            
            flash(f"Welcome, Admin {result['admin'].username}!", 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash(result['message'], 'danger')
            return render_template('auth/admin_login.html')
    
    return render_template('auth/admin_login.html')


@auth_bp.route('/logout')
def logout():
    """Logout user or admin."""
    if 'user_id' in session:
        username = session.get('username', 'User')
        session.clear()
        flash(f'Goodbye, {username}! You have been logged out.', 'info')
        return redirect(url_for('home'))
    elif 'admin_id' in session:
        username = session.get('admin_username', 'Admin')
        session.clear()
        flash(f'Admin {username} logged out successfully.', 'info')
        return redirect(url_for('auth.admin_login'))
    else:
        return redirect(url_for('home'))
