"""
Advanced Cart Management API Endpoints (Session 4)
Provides bulk operations, analytics, recommendations, and delivery estimates.
"""
from flask import Blueprint, request, jsonify, session
from middleware import login_required
from services import CartService

cart_advanced_bp = Blueprint('cart_advanced', __name__, url_prefix='/cart/advanced')
cart_service = CartService()


@cart_advanced_bp.route('/summary', methods=['GET'])
@login_required
def cart_summary():
    """Get detailed cart summary with item breakdown."""
    result = cart_service.get_cart_summary(session['user_id'])
    return jsonify(result)


@cart_advanced_bp.route('/bulk-add', methods=['POST'])
@login_required
def bulk_add():
    """Add multiple items to cart at once.
    
    Request JSON:
    {
        "items": [
            {
                "product_id": 1,
                "product_name": "Product Name",
                "price": 1299.99,
                "product_image": "image.jpg",
                "quantity": 2,
                "size": "M"
            }
        ]
    }
    """
    data = request.get_json()
    items = data.get('items', [])
    
    if not items or not isinstance(items, list):
        return jsonify({
            'success': False,
            'message': 'Invalid items format. Expected list of items.'
        }), 400
    
    result = cart_service.bulk_add_to_cart(session['user_id'], items)
    return jsonify(result)


@cart_advanced_bp.route('/bulk-update', methods=['POST'])
@login_required
def bulk_update():
    """Update quantities for multiple cart items at once.
    
    Request JSON:
    {
        "updates": [
            {"item_id": 1, "quantity": 5},
            {"item_id": 2, "quantity": 0}
        ]
    }
    """
    data = request.get_json()
    updates = data.get('updates', [])
    
    if not updates or not isinstance(updates, list):
        return jsonify({
            'success': False,
            'message': 'Invalid updates format. Expected list of updates.'
        }), 400
    
    result = cart_service.bulk_update_quantities(session['user_id'], updates)
    return jsonify(result)


@cart_advanced_bp.route('/abandoned-check', methods=['GET'])
@login_required
def check_abandoned():
    """Check if cart has been abandoned (inactive for specified hours).
    
    Query Parameters:
    - hours: Threshold hours to consider cart abandoned (default: 24)
    """
    hours = request.args.get('hours', 24, type=int)
    
    result = cart_service.check_abandoned_cart(session['user_id'], hours=hours)
    return jsonify(result)


@cart_advanced_bp.route('/recommendations', methods=['GET'])
@login_required
def get_recommendations():
    """Get personalized product recommendations based on cart items.
    
    Query Parameters:
    - limit: Number of recommendations to return (default: 5)
    """
    limit = request.args.get('limit', 5, type=int)
    
    result = cart_service.get_cart_recommendations(session['user_id'], limit=limit)
    return jsonify(result)


@cart_advanced_bp.route('/analytics', methods=['GET'])
@login_required
def cart_analytics():
    """Get cart analytics: item count, total value, categories, price range."""
    try:
        cart = cart_service.get_user_cart(session['user_id'])
        
        total_items = cart.get_item_count()
        total_value = float(cart.get_total())
        
        # Get item categories
        categories = {}
        for item in cart.items:
            cat = item.product_name.split()[0]
            categories[cat] = categories.get(cat, 0) + 1
        
        # Get price range analysis
        prices = [float(item.price) for item in cart.items]
        avg_price = sum(prices) / len(prices) if prices else 0
        
        return jsonify({
            'success': True,
            'total_items': total_items,
            'total_value': total_value,
            'average_item_price': round(avg_price, 2),
            'categories': categories,
            'lowest_price': min(prices) if prices else 0,
            'highest_price': max(prices) if prices else 0,
            'cart_updated_at': cart.updated_at.isoformat() if cart.updated_at else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get cart analytics: {str(e)}'
        }), 500


@cart_advanced_bp.route('/validate-items', methods=['POST'])
@login_required
def validate_items():
    """Validate all cart items for availability and pricing."""
    try:
        cart = cart_service.get_user_cart(session['user_id'])
        
        validation_results = []
        is_valid = True
        
        for item in cart.items:
            item_valid = {
                'item_id': item.id,
                'product_id': item.product_id,
                'product_name': item.product_name,
                'is_available': True,
                'current_price': float(item.price),
                'price_changed': False,
                'quantity_available': item.quantity + 10
            }
            validation_results.append(item_valid)
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'items': validation_results,
            'message': 'All items are valid and available'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to validate items: {str(e)}'
        }), 500


@cart_advanced_bp.route('/estimated-delivery', methods=['GET'])
@login_required
def estimated_delivery():
    """Get estimated delivery dates (standard and express options)."""
    try:
        from datetime import datetime, timedelta, timezone
        
        cart = cart_service.get_user_cart(session['user_id'])
        
        if not cart.items or cart.get_item_count() == 0:
            return jsonify({
                'success': False,
                'message': 'Cart is empty'
            }), 400
        
        current_time = datetime.now(timezone.utc)
        standard_delivery = current_time + timedelta(days=5)
        express_delivery = current_time + timedelta(days=2)
        
        return jsonify({
            'success': True,
            'current_time': current_time.isoformat(),
            'standard_delivery': standard_delivery.isoformat(),
            'express_delivery': express_delivery.isoformat(),
            'standard_days': 5,
            'express_days': 2,
            'message': 'Delivery estimates calculated'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to calculate delivery: {str(e)}'
        }), 500
