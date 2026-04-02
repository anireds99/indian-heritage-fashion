"""
Cart controller for shopping cart and checkout operations.
Implements Controller pattern following SOLID principles.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from middleware import login_required
from services import CartService, CheckoutService
from repositories import AddressRepository
import traceback

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


# Session 6 - Amazon-style Product Detail View
@cart_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """View full product detail (Amazon style) - publicly accessible."""
    try:
        # Product data catalog
        products = {
            1: {
                'id': 1,
                'name': 'Tanjore Temple Graphic Tee',
                'price': 1299.99,
                'image': '/static/images/mockups/tanjore.jpg',
                'rating': 4.5,
                'reviews': 128,
                'description': 'Celebrate the artistic heritage of Tanjore with this beautifully crafted graphic tee. Featuring intricate temple designs inspired by the golden art form of Tanjore paintings.',
                'features': [
                    '100% premium cotton fabric',
                    'High-quality print technology',
                    'Comfortable and breathable',
                    'Machine washable',
                    'Made in India'
                ],
                'colors': ['Black', 'Navy Blue', 'White'],
                'sizes': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                'stock': 15,
                'category': 'Tees'
            },
            2: {
                'id': 2,
                'name': 'ISRO Space Missions Hoodie',
                'price': 1999.99,
                'image': '/static/images/mockups/isro_1st_rocket.jpg',
                'rating': 4.8,
                'reviews': 256,
                'description': 'Inspired by India\'s incredible space journey with ISRO. This premium hoodie celebrates our achievements in space exploration with stunning graphic design.',
                'features': [
                    '80% cotton, 20% polyester blend',
                    'Soft fleece interior',
                    'Double-stitched for durability',
                    'Front kangaroo pocket',
                    'Adjustable drawstring hood'
                ],
                'colors': ['Black', 'Grey', 'Navy'],
                'sizes': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                'stock': 8,
                'category': 'Hoodies'
            },
            3: {
                'id': 3,
                'name': 'Hampi Ruins Heritage Tee',
                'price': 1399.99,
                'image': '/static/images/mockups/hampi_temple_tshirt.jpg',
                'rating': 4.6,
                'reviews': 89,
                'description': 'Journey through the magnificent ruins of Hampi with this heritage-inspired graphic tee.',
                'features': [
                    '100% organic cotton',
                    'Eco-friendly printing process',
                    'Vintage-inspired design',
                    'Comfortable relaxed fit',
                    'Fair trade certified'
                ],
                'colors': ['Sand', 'Olive', 'Charcoal'],
                'sizes': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                'stock': 12,
                'category': 'Tees'
            },
            4: {
                'id': 4,
                'name': 'Mysore Palace Heritage Tee',
                'price': 1499.99,
                'image': '/static/images/mockups/mysore.jpg',
                'rating': 4.7,
                'reviews': 95,
                'description': 'Celebrate the majestic Mysore Palace with this stunning heritage design.',
                'features': [
                    '100% premium cotton',
                    'High-quality print',
                    'Comfortable fit',
                    'Available in multiple sizes',
                    'Perfect gift for heritage lovers'
                ],
                'colors': ['Black', 'White', 'Navy'],
                'sizes': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                'stock': 10,
                'category': 'Tees'
            },
            5: {
                'id': 5,
                'name': 'Hyderabad Charminar Heritage Tee',
                'price': 1499.99,
                'image': '/static/images/mockups/hyderabad.jpg',
                'rating': 4.6,
                'reviews': 78,
                'description': 'Tribute to the iconic Charminar with this beautifully designed heritage tee.',
                'features': [
                    '100% premium cotton',
                    'Vibrant colors',
                    'Comfortable relaxed fit',
                    'Perfect for heritage lovers',
                    'Sustainable production'
                ],
                'colors': ['Black', 'Grey', 'White'],
                'sizes': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
                'stock': 9,
                'category': 'Tees'
            }
        }
        
        # Get product or return 404
        product = products.get(product_id)
        
        if not product:
            flash('Product not found', 'danger')
            return redirect(url_for('shop'))
        
        return render_template('cart/product_detail.html', product=product)
    
    except Exception as e:
        print(f"[ERROR] product_detail endpoint failed: {str(e)}")
        print(traceback.format_exc())
        flash('Error loading product details. Please try again.', 'danger')
        return redirect(url_for('shop'))
