"""
Admin controller for administrative dashboard and management.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from middleware import admin_required, super_admin_required
from services import AdminService
from repositories import OrderRepository, UserRepository

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
admin_service = AdminService()


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with statistics and overview."""
    from models import User, Order, db
    
    # Get statistics
    total_users = db.session.query(User).count()
    total_orders = db.session.query(Order).count()
    pending_orders = db.session.query(Order).filter_by(status='pending').count()
    
    # Get recent orders
    recent_orders = OrderRepository.find_all(page=1, per_page=10)
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         recent_orders=recent_orders.items)


@admin_bp.route('/users')
@admin_required
def users():
    """Manage all users."""
    page = request.args.get('page', 1, type=int)
    users_pagination = admin_service.get_all_users(page=page, per_page=20)
    
    return render_template('admin/users.html', users=users_pagination)


@admin_bp.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    """View user details."""
    user = UserRepository.find_by_id(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('admin.users'))
    
    # Get user orders
    orders = OrderRepository.find_by_user(user_id, page=1, per_page=10)
    
    return render_template('admin/user_detail.html', user=user, orders=orders.items)


@admin_bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(user_id):
    """Deactivate a user account."""
    result = admin_service.deactivate_user(user_id)
    flash(result['message'], 'success' if result['success'] else 'danger')
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/users/<int:user_id>/activate', methods=['POST'])
@admin_required
def activate_user(user_id):
    """Activate a user account."""
    result = admin_service.activate_user(user_id)
    flash(result['message'], 'success' if result['success'] else 'danger')
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/orders')
@admin_required
def orders():
    """View and manage all orders."""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    if status_filter != 'all':
        from models import Order
        orders_pagination = Order.query.filter_by(status=status_filter).order_by(
            Order.created_at.desc()
        ).paginate(page=page, per_page=20, error_out=False)
    else:
        orders_pagination = OrderRepository.find_all(page=page, per_page=20)
    
    return render_template('admin/orders.html', orders=orders_pagination, status_filter=status_filter)


@admin_bp.route('/orders/<int:order_id>')
@admin_required
def order_detail(order_id):
    """View order details."""
    order = OrderRepository.find_by_id(order_id)
    if not order:
        flash('Order not found', 'danger')
        return redirect(url_for('admin.orders'))
    
    return render_template('admin/order_detail.html', order=order)


@admin_bp.route('/orders/<int:order_id>/update-status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """Update order status."""
    order = OrderRepository.find_by_id(order_id)
    if not order:
        flash('Order not found', 'danger')
        return redirect(url_for('admin.orders'))
    
    new_status = request.form.get('status')
    if new_status in ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']:
        OrderRepository.update_status(order, new_status)
        flash(f'Order status updated to {new_status}', 'success')
    else:
        flash('Invalid status', 'danger')
    
    return redirect(url_for('admin.order_detail', order_id=order_id))


@admin_bp.route('/admins')
@super_admin_required
def admins():
    """Manage all admins (super admin only)."""
    all_admins = admin_service.get_all_admins()
    return render_template('admin/admins.html', admins=all_admins)


@admin_bp.route('/settings')
@admin_required
def settings():
    """Admin settings page."""
    from repositories import AdminRepository
    admin = AdminRepository.find_by_id(session['admin_id'])
    return render_template('admin/settings.html', admin=admin)
