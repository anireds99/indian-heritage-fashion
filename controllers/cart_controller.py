"""
Cart controller for shopping cart and checkout operations.
Implements Controller pattern following SOLID principles.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from middleware import login_required
from services import CartService, CheckoutService
from repositories import AddressRepository

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')
cart_service = CartService()
checkout_service = CheckoutService()


@cart_bp.route('/')
@login_required
def view_cart():
    """View shopping cart."""
    cart = cart_service.get_user_cart(session['user_id'])
    return render_template('cart/cart.html', cart=cart)


@cart_bp.route('/add', methods=['POST'])
@login_required
def add_to_cart():
    """Add item to cart."""
    product_id = request.form.get('product_id', type=int)
    product_name = request.form.get('product_name')
    price = request.form.get('price', type=float)
    product_image = request.form.get('product_image')
    quantity = request.form.get('quantity', 1, type=int)
    size = request.form.get('size', 'M')
    
    result = cart_service.add_to_cart(
        session['user_id'],
        product_id,
        product_name,
        price,
        product_image,
        quantity,
        size
    )
    
    if request.is_json or request.form.get('ajax'):
        return jsonify(result)
    
    flash(result['message'], 'success' if result['success'] else 'danger')
    return redirect(request.referrer or url_for('shop'))


@cart_bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update_item(item_id):
    """Update cart item quantity."""
    quantity = request.form.get('quantity', type=int)
    
    result = cart_service.update_cart_item(item_id, quantity)
    
    if request.is_json:
        return jsonify(result)
    
    flash(result['message'], 'success' if result['success'] else 'danger')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_item(item_id):
    """Remove item from cart."""
    result = cart_service.remove_from_cart(item_id)
    
    if request.is_json:
        return jsonify(result)
    
    flash(result['message'], 'success' if result['success'] else 'danger')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/clear', methods=['POST'])
@login_required
def clear_cart():
    """Clear all items from cart."""
    result = cart_service.clear_cart(session['user_id'])
    flash(result['message'], 'success' if result['success'] else 'danger')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/checkout')
@login_required
def checkout():
    """Checkout page."""
    cart = cart_service.get_user_cart(session['user_id'])
    
    if not cart.items.count():
        flash('Your cart is empty', 'warning')
        return redirect(url_for('shop'))
    
    addresses = AddressRepository.find_by_user(session['user_id'])
    
    return render_template('cart/checkout.html', cart=cart, addresses=addresses)


@cart_bp.route('/process-checkout', methods=['POST'])
@login_required
def process_checkout():
    """Process checkout and create order."""
    address_id = request.form.get('address_id', type=int)
    payment_method = request.form.get('payment_method')
    
    if not address_id:
        flash('Please select a shipping address', 'danger')
        return redirect(url_for('cart.checkout'))
    
    if not payment_method or payment_method not in ['cod', 'card']:
        flash('Please select a valid payment method', 'danger')
        return redirect(url_for('cart.checkout'))
    
    card_details = None
    if payment_method == 'card':
        card_details = {
            'card_number': request.form.get('card_number'),
            'card_name': request.form.get('card_name'),
            'expiry_month': request.form.get('expiry_month'),
            'expiry_year': request.form.get('expiry_year'),
            'cvv': request.form.get('cvv')
        }
    
    result = checkout_service.create_order_from_cart(
        session['user_id'],
        address_id,
        payment_method,
        card_details
    )
    
    if result['success']:
        flash(f"Order placed successfully! Order Number: {result['order_number']}", 'success')
        return redirect(url_for('cart.order_success', order_id=result['order'].id))
    else:
        flash(result['message'], 'danger')
        return redirect(url_for('cart.checkout'))


@cart_bp.route('/order-success/<int:order_id>')
@login_required
def order_success(order_id):
    """Order success page."""
    from repositories import OrderRepository
    order = OrderRepository.find_by_id(order_id)
    
    if not order or order.user_id != session['user_id']:
        flash('Order not found', 'danger')
        return redirect(url_for('user.dashboard'))
    
    return render_template('cart/order_success.html', order=order)
