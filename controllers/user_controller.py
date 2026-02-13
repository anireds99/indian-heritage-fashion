"""
User controller for customer dashboard and profile management.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from middleware import login_required
from services import UserService
from repositories import OrderRepository, AddressRepository

user_bp = Blueprint('user', __name__, url_prefix='/user')
user_service = UserService()


@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing orders and profile summary."""
    user = user_service.get_user_profile(session['user_id'])
    
    # Get recent orders
    orders_pagination = OrderRepository.find_by_user(session['user_id'], page=1, per_page=5)
    
    # Get addresses
    addresses = AddressRepository.find_by_user(session['user_id'])
    
    return render_template('user/dashboard.html', 
                         user=user, 
                         orders=orders_pagination.items,
                         addresses=addresses)


@user_bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    user = user_service.get_user_profile(session['user_id'])
    return render_template('user/profile.html', user=user)


@user_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile."""
    user = user_service.get_user_profile(session['user_id'])
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        result = user_service.update_profile(
            session['user_id'],
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('user.profile'))
        else:
            flash(result['message'], 'danger')
    
    return render_template('user/edit_profile.html', user=user)


@user_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password."""
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return render_template('user/change_password.html')
        
        result = user_service.change_password(
            session['user_id'],
            old_password,
            new_password
        )
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('user.profile'))
        else:
            flash(result['message'], 'danger')
    
    return render_template('user/change_password.html')


@user_bp.route('/orders')
@login_required
def orders():
    """View all user orders."""
    page = request.args.get('page', 1, type=int)
    orders_pagination = OrderRepository.find_by_user(session['user_id'], page=page, per_page=10)
    
    return render_template('user/orders.html', orders=orders_pagination)


@user_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    """View order details."""
    order = OrderRepository.find_by_id(order_id)
    
    if not order or order.user_id != session['user_id']:
        flash('Order not found', 'danger')
        return redirect(url_for('user.orders'))
    
    return render_template('user/order_detail.html', order=order)


@user_bp.route('/addresses')
@login_required
def addresses():
    """View and manage addresses."""
    user_addresses = AddressRepository.find_by_user(session['user_id'])
    return render_template('user/addresses.html', addresses=user_addresses)


@user_bp.route('/addresses/add', methods=['GET', 'POST'])
@login_required
def add_address():
    """Add new shipping address."""
    if request.method == 'POST':
        try:
            AddressRepository.create(
                user_id=session['user_id'],
                full_name=request.form.get('full_name'),
                phone=request.form.get('phone'),
                address_line1=request.form.get('address_line1'),
                address_line2=request.form.get('address_line2'),
                city=request.form.get('city'),
                state=request.form.get('state'),
                postal_code=request.form.get('postal_code'),
                country=request.form.get('country', 'India'),
                is_default=bool(request.form.get('is_default'))
            )
            flash('Address added successfully', 'success')
            return redirect(url_for('user.addresses'))
        except Exception as e:
            flash(f'Failed to add address: {str(e)}', 'danger')
    
    return render_template('user/add_address.html')
