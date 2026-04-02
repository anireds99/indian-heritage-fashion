"""
Enhanced Authentication Controller with password reset, logout tracking, and session management.
Implements Controller pattern following SOLID principles.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from services import AuthenticationService
from services.auth_service import EnhancedAuthenticationService, EmailService, get_client_info
from middleware import guest_only, login_required
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_service = AuthenticationService()
enhanced_auth_service = EnhancedAuthenticationService()
email_service = EmailService()


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
    """User login page and handler with session tracking."""
    if request.method == 'POST':
        identifier = request.form.get('identifier')  # email or username
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        logger.info(f"Login attempt for identifier: {identifier}")
        
        result = auth_service.login_user(identifier, password)
        
        logger.info(f"Login result: {result['success']}, Message: {result['message']}")
        
        if result['success']:
            user = result['user']
            
            # Get client info for tracking
            client_info = get_client_info(request)
            
            # Record login in history
            login_record = enhanced_auth_service.record_login_attempt(
                user_id=user.id,
                success=True,
                ip_address=client_info['ip_address'],
                user_agent=client_info['user_agent']
            )
            
            # Create session
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_email'] = user.email
            session['login_record_id'] = login_record.id if login_record else None
            
            # Remember me functionality - extends session
            if remember:
                session.permanent = True
                from datetime import timedelta
                session.permanent_timeout = timedelta(days=30)
            
            flash(f"Welcome back, {user.username}!", 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page or url_for('user.dashboard'))
        else:
            # Record failed login attempt
            from repositories import UserRepository
            user_repo = UserRepository()
            user = user_repo.find_by_email(identifier) or user_repo.find_by_username(identifier)
            
            if user:
                client_info = get_client_info(request)
                enhanced_auth_service.record_login_attempt(
                    user_id=user.id,
                    success=False,
                    ip_address=client_info['ip_address'],
                    user_agent=client_info['user_agent'],
                    failure_reason=result['message']
                )
            
            flash(result['message'], 'danger')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@guest_only
def forgot_password():
    """Forgot password page - request password reset."""
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Please enter your email address', 'danger')
            return render_template('auth/forgot_password.html')
        
        # Generate reset token
        result = enhanced_auth_service.generate_password_reset_token(email)
        
        if result['success']:
            # Prepare reset link
            token = result.get('token')
            if token:
                reset_link = url_for('auth.reset_password', token=token, _external=True)
                
                # Send email (in production, integrate with actual email service)
                email_result = email_service.send_password_reset_email(
                    user=result.get('user'),
                    reset_token=token,
                    reset_link=reset_link
                )
                
                logger.info(f"Password reset email sent to {email}")
            
            # Always show success message for security (don't reveal if email exists)
            flash('If an account exists with this email, a password reset link will be sent shortly.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash(result['message'], 'danger')
            return render_template('auth/forgot_password.html')
    
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@guest_only
def reset_password(token):
    """Reset password page with valid token."""
    # Validate token on GET
    validation = enhanced_auth_service.validate_reset_token(token)
    
    if not validation['success']:
        flash(validation['message'], 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate passwords match
        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        # Reset password
        result = enhanced_auth_service.reset_password_with_token(token, new_password)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(result['message'], 'danger')
            return render_template('auth/reset_password.html', token=token)
    
    return render_template('auth/reset_password.html', token=token)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user and clear session."""
    user_id = session.get('user_id')
    username = session.get('username', 'User')
    login_record_id = session.get('login_record_id')
    
    # Record logout in history
    if user_id:
        enhanced_auth_service.record_logout(user_id)
        logger.info(f"User {username} (ID: {user_id}) logged out")
    
    # Clear session
    session.clear()
    
    flash(f'Goodbye, {username}! You have been logged out.', 'info')
    return redirect(url_for('home'))


@auth_bp.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    """Admin registration page (restricted - requires special token or super admin)."""
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


@auth_bp.route('/admin/logout')
def admin_logout():
    """Logout admin and clear session."""
    admin_username = session.get('admin_username', 'Admin')
    session.clear()
    flash(f'Admin {admin_username} logged out successfully.', 'info')
    return redirect(url_for('auth.admin_login'))


# ==================== API ENDPOINTS ====================

@auth_bp.route('/api/login-history', methods=['GET'])
@login_required
def api_login_history():
    """Get user's login history (API endpoint)."""
    user_id = session.get('user_id')
    limit = request.args.get('limit', 10, type=int)
    
    result = enhanced_auth_service.get_login_history(user_id, limit)
    return jsonify(result)


@auth_bp.route('/api/change-password', methods=['POST'])
@login_required
def api_change_password():
    """Change password for logged-in user (API endpoint)."""
    from services import UserService
    
    user_id = session.get('user_id')
    data = request.get_json()
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    # Validate inputs
    if not all([old_password, new_password, confirm_password]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'New passwords do not match'}), 400
    
    # Change password
    user_service = UserService()
    result = user_service.change_password(user_id, old_password, new_password)
    
    if result['success']:
        # Send confirmation email
        from repositories import UserRepository
        user_repo = UserRepository()
        user = user_repo.find_by_id(user_id)
        if user:
            email_service.send_password_changed_email(user)
    
    return jsonify(result)


@auth_bp.route('/api/validate-reset-token/<token>', methods=['GET'])
def api_validate_reset_token(token):
    """Validate password reset token (API endpoint)."""
    result = enhanced_auth_service.validate_reset_token(token)
    return jsonify(result)
