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
    """Add item to shopping cart."""
    data = request.get_json()
    
    result = cart_service.add_to_cart(
        user_id=session['user_id'],
        product_id=data.get('product_id'),
        product_name=data.get('product_name'),
        price=data.get('price'),
        product_image=data.get('product_image'),
        quantity=data.get('quantity', 1),
        size=data.get('size', 'M')
    )
    
    return jsonify(result)


@cart_bp.route('/count')
@login_required
def cart_count():
    """Get cart item count."""
    try:
        cart = cart_service.get_user_cart(session['user_id'])
        return jsonify({
            'success': True,
            'count': cart.get_item_count()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


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


@cart_bp.route('/validate-coupon', methods=['POST'])
@login_required
def validate_coupon():
    """Validate coupon code API endpoint."""
    from services import DiscountService
    
    data = request.get_json()
    coupon_code = data.get('coupon_code', '').strip()
    cart_total = data.get('cart_total', 0)
    
    if not coupon_code:
        return jsonify({
            'success': False,
            'message': 'Please enter a coupon code'
        })
    
    if not cart_total or cart_total <= 0:
        return jsonify({
            'success': False,
            'message': 'Invalid cart total'
        })
    
    discount_service = DiscountService()
    result = discount_service.validate_coupon(
        coupon_code,
        cart_total,
        session['user_id']
    )
    
    return jsonify(result)


@cart_bp.route('/apply-coupon/<int:order_id>', methods=['POST'])
@login_required
def apply_coupon(order_id):
    """Apply coupon to order."""
    from services import DiscountService
    from repositories import OrderRepository
    
    order = OrderRepository.find_by_id(order_id)
    if not order or order.user_id != session['user_id']:
        return jsonify({
            'success': False,
            'message': 'Order not found'
        })
    
    data = request.get_json()
    coupon_code = data.get('coupon_code', '').strip()
    
    if not coupon_code:
        return jsonify({
            'success': False,
            'message': 'Please enter a coupon code'
        })
    
    discount_service = DiscountService()
    result = discount_service.apply_coupon_to_order(
        coupon_code,
        order,
        session['user_id']
    )
    
    return jsonify(result)
