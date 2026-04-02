"""
Service layer for business logic operations.
Implements Service Pattern following SOLID principles.
"""
from typing import Optional, Dict, Any
from repositories import UserRepository, AdminRepository, CartRepository, CartItemRepository, OrderRepository, PaymentRepository
from models import User, Admin, Cart, Order, OrderItem, db


class AuthenticationService:
    """Service for authentication operations."""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.admin_repo = AdminRepository()
    
    def register_user(self, email: str, username: str, password: str, **kwargs) -> Dict[str, Any]:
        """
        Register a new user.
        Returns: {'success': bool, 'message': str, 'user': User (optional)}
        """
        # Validate email
        if self.user_repo.email_exists(email):
            return {'success': False, 'message': 'Email already registered'}
        
        # Validate username
        if self.user_repo.username_exists(username):
            return {'success': False, 'message': 'Username already taken'}
        
        # Validate password strength
        if len(password) < 6:
            return {'success': False, 'message': 'Password must be at least 6 characters'}
        
        try:
            user = self.user_repo.create(email, username, password, **kwargs)
            return {
                'success': True,
                'message': 'Registration successful',
                'user': user
            }
        except Exception as e:
            return {'success': False, 'message': f'Registration failed: {str(e)}'}
    
    def login_user(self, identifier: str, password: str) -> Dict[str, Any]:
        """
        Login user with email/username and password.
        Returns: {'success': bool, 'message': str, 'user': User (optional)}
        """
        # Enhanced logging for debugging
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        logger.info(f"Login attempt - Identifier: {identifier}")
        
        # Try to find user by email or username
        user = self.user_repo.find_by_email(identifier)
        if not user:
            user = self.user_repo.find_by_username(identifier)
        
        if not user:
            logger.warning(f"User not found: {identifier}")
            return {'success': False, 'message': 'Invalid email/username or password. Please check your credentials.'}
        
        logger.info(f"User found: {user.username} (ID: {user.id})")
        
        if not user.is_active:
            logger.warning(f"Inactive user attempted login: {user.username}")
            return {'success': False, 'message': 'Your account has been deactivated. Please contact support.'}
        
        # Verify password
        password_valid = user.check_password(password)
        logger.info(f"Password verification result: {password_valid}")
        
        if not password_valid:
            logger.warning(f"Invalid password for user: {user.username}")
            return {'success': False, 'message': 'Invalid email/username or password. Please check your credentials.'}
        
        user.update_last_login()
        logger.info(f"Login successful for user: {user.username}")
        
        return {
            'success': True,
            'message': 'Login successful',
            'user': user
        }
    
    def register_admin(self, email: str, username: str, password: str, **kwargs) -> Dict[str, Any]:
        """
        Register a new admin.
        Returns: {'success': bool, 'message': str, 'admin': Admin (optional)}
        """
        # Check if email exists
        if self.admin_repo.find_by_email(email):
            return {'success': False, 'message': 'Email already registered'}
        
        # Check if username exists
        if self.admin_repo.find_by_username(username):
            return {'success': False, 'message': 'Username already taken'}
        
        # Validate password strength
        if len(password) < 8:
            return {'success': False, 'message': 'Admin password must be at least 8 characters'}
        
        try:
            admin = self.admin_repo.create(email, username, password, **kwargs)
            return {
                'success': True,
                'message': 'Admin registration successful',
                'admin': admin
            }
        except Exception as e:
            return {'success': False, 'message': f'Registration failed: {str(e)}'}
    
    def login_admin(self, identifier: str, password: str) -> Dict[str, Any]:
        """
        Login admin with email/username and password.
        Returns: {'success': bool, 'message': str, 'admin': Admin (optional)}
        """
        # Try to find admin by email or username
        admin = self.admin_repo.find_by_email(identifier)
        if not admin:
            admin = self.admin_repo.find_by_username(identifier)
        
        if not admin:
            return {'success': False, 'message': 'Invalid admin credentials'}
        
        if not admin.is_active:
            return {'success': False, 'message': 'Admin account is deactivated'}
        
        if not admin.check_password(password):
            return {'success': False, 'message': 'Invalid admin credentials'}
        
        admin.update_last_login()
        
        return {
            'success': True,
            'message': 'Admin login successful',
            'admin': admin
        }


class UserService:
    """Service for user management operations."""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    def get_user_profile(self, user_id: int) -> Optional[User]:
        """Get user profile by ID."""
        return self.user_repo.find_by_id(user_id)
    
    def update_profile(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """Update user profile."""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        try:
            # Don't allow updating email/username through this method
            kwargs.pop('email', None)
            kwargs.pop('username', None)
            kwargs.pop('password_hash', None)
            
            updated_user = self.user_repo.update(user, **kwargs)
            return {
                'success': True,
                'message': 'Profile updated successfully',
                'user': updated_user
            }
        except Exception as e:
            return {'success': False, 'message': f'Update failed: {str(e)}'}
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password."""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        if not user.check_password(old_password):
            return {'success': False, 'message': 'Current password is incorrect'}
        
        if len(new_password) < 6:
            return {'success': False, 'message': 'New password must be at least 6 characters'}
        
        try:
            user.set_password(new_password)
            self.user_repo.update(user)
            return {'success': True, 'message': 'Password changed successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Password change failed: {str(e)}'}


class AdminService:
    """Service for admin operations."""
    
    def __init__(self):
        self.admin_repo = AdminRepository()
        self.user_repo = UserRepository()
    
    def get_all_users(self, page: int = 1, per_page: int = 20):
        """Get all users with pagination."""
        return self.user_repo.find_all(page, per_page)
    
    def get_all_admins(self):
        """Get all admins."""
        return self.admin_repo.find_all()
    
    def deactivate_user(self, user_id: int) -> Dict[str, Any]:
        """Deactivate a user account."""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        try:
            self.user_repo.update(user, is_active=False)
            return {'success': True, 'message': 'User deactivated successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Deactivation failed: {str(e)}'}
    
    def activate_user(self, user_id: int) -> Dict[str, Any]:
        """Activate a user account."""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        try:
            self.user_repo.update(user, is_active=True)
            return {'success': True, 'message': 'User activated successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Activation failed: {str(e)}'}


class CartService:
    """Service for shopping cart operations."""
    
    def __init__(self):
        self.cart_repo = CartRepository()
        self.cart_item_repo = CartItemRepository()
    
    def get_user_cart(self, user_id: int) -> Cart:
        """Get or create user's cart."""
        return self.cart_repo.find_or_create_by_user(user_id)
    
    def add_to_cart(self, user_id: int, product_id: int, product_name: str, 
                   price: float, product_image: str, quantity: int = 1, size: str = 'M') -> Dict[str, Any]:
        """Add item to cart."""
        try:
            cart = self.get_user_cart(user_id)
            self.cart_item_repo.add_item(
                cart.id, product_id, product_name, price, 
                product_image, quantity, size
            )
            return {
                'success': True,
                'message': 'Item added to cart',
                'cart_count': cart.get_item_count()
            }
        except Exception as e:
            return {'success': False, 'message': f'Failed to add item: {str(e)}'}
    
    def update_cart_item(self, item_id: int, quantity: int) -> Dict[str, Any]:
        """Update cart item quantity."""
        try:
            cart_item = self.cart_item_repo.find_by_id(item_id)
            if not cart_item:
                return {'success': False, 'message': 'Cart item not found'}
            
            if quantity <= 0:
                self.cart_item_repo.remove_item(cart_item)
                return {'success': True, 'message': 'Item removed from cart'}
            
            self.cart_item_repo.update_quantity(cart_item, quantity)
            return {'success': True, 'message': 'Cart updated'}
        except Exception as e:
            return {'success': False, 'message': f'Failed to update cart: {str(e)}'}
    
    def remove_from_cart(self, item_id: int) -> Dict[str, Any]:
        """Remove item from cart."""
        try:
            cart_item = self.cart_item_repo.find_by_id(item_id)
            if not cart_item:
                return {'success': False, 'message': 'Cart item not found'}
            
            self.cart_item_repo.remove_item(cart_item)
            return {'success': True, 'message': 'Item removed from cart'}
        except Exception as e:
            return {'success': False, 'message': f'Failed to remove item: {str(e)}'}
    
    def clear_cart(self, user_id: int) -> Dict[str, Any]:
        """Clear all items from cart."""
        try:
            cart = self.get_user_cart(user_id)
            self.cart_repo.clear_cart(cart)
            return {'success': True, 'message': 'Cart cleared'}
        except Exception as e:
            return {'success': False, 'message': f'Failed to clear cart: {str(e)}'}


class CheckoutService:
    """Service for checkout and payment operations."""
    
    def __init__(self):
        self.cart_repo = CartRepository()
        self.order_repo = OrderRepository()
        self.payment_repo = PaymentRepository()
    
    def create_order_from_cart(self, user_id: int, shipping_address_id: int, 
                               payment_method: str, card_details: Dict = None) -> Dict[str, Any]:
        """Create order from cart items."""
        try:
            # Get cart
            cart = self.cart_repo.find_or_create_by_user(user_id)
            
            if not cart.items.count():
                return {'success': False, 'message': 'Cart is empty'}
            
            # Calculate total
            total_amount = cart.get_total()
            
            # Create order
            order = self.order_repo.create(
                user_id=user_id,
                total_amount=total_amount,
                shipping_address_id=shipping_address_id,
                status='pending'
            )
            
            # Create order items from cart
            for cart_item in cart.items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    product_name=cart_item.product_name,
                    quantity=cart_item.quantity,
                    price=cart_item.price,
                    size=cart_item.size
                )
                db.session.add(order_item)
            
            # Create payment record
            payment = self.payment_repo.create(
                order_id=order.id,
                payment_method=payment_method,
                amount=total_amount
            )
            
            # Process payment based on method
            if payment_method == 'cod':
                # COD - Order confirmed immediately
                order.status = 'confirmed'
                payment.payment_status = 'pending'  # Payment on delivery
            elif payment_method == 'card':
                # Simulate card payment processing
                payment_result = self._process_card_payment(card_details, total_amount)
                if payment_result['success']:
                    payment.payment_status = 'completed'
                    payment.transaction_id = payment_result['transaction_id']
                    payment.card_last4 = card_details.get('card_number', '')[-4:]
                    order.status = 'confirmed'
                else:
                    payment.payment_status = 'failed'
                    order.status = 'cancelled'
                    db.session.commit()
                    return {
                        'success': False,
                        'message': 'Payment failed: ' + payment_result.get('message', 'Unknown error')
                    }
            
            db.session.commit()
            
            # Clear cart after successful order
            self.cart_repo.clear_cart(cart)
            
            return {
                'success': True,
                'message': 'Order placed successfully',
                'order': order,
                'order_number': order.order_number
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Order creation failed: {str(e)}'}
    
    def _process_card_payment(self, card_details: Dict, amount: float) -> Dict[str, Any]:
        """
        Process card payment (simplified simulation).
        In production, integrate with payment gateway like Razorpay, Stripe, etc.
        """
        import secrets
        
        # Simulate payment processing
        # In production, call actual payment gateway API
        
        card_number = card_details.get('card_number', '')
        cvv = card_details.get('cvv', '')
        
        # Basic validation
        if len(card_number.replace(' ', '')) != 16:
            return {'success': False, 'message': 'Invalid card number'}
        
        if len(cvv) != 3:
            return {'success': False, 'message': 'Invalid CVV'}
        
        # Simulate successful payment
        transaction_id = f"TXN-{secrets.token_hex(8).upper()}"
        
        return {
            'success': True,
            'transaction_id': transaction_id,
            'message': 'Payment successful'
        }


class DiscountService:
    """Service for discount and coupon operations."""
    
    def __init__(self):
        from repositories import CouponRepository
        self.coupon_repo = CouponRepository()
    
    def validate_coupon(self, code: str, cart_total: float, user_id: int = None) -> Dict[str, Any]:
        """Validate coupon code and calculate discount."""
        if not code or not code.strip():
            return {'success': False, 'message': 'Please enter a coupon code'}
        
        try:
            validation_result = self.coupon_repo.validate_coupon(code.upper(), cart_total, user_id)
            
            if validation_result['valid']:
                return {
                    'success': True,
                    'message': validation_result['message'],
                    'coupon_code': code.upper(),
                    'discount_amount': validation_result['discount_amount'],
                    'final_amount': validation_result['final_amount'],
                    'discount_type': validation_result['coupon']['discount_type'],
                    'discount_value': validation_result['coupon']['discount_value']
                }
            else:
                return {
                    'success': False,
                    'message': validation_result['message']
                }
        except Exception as e:
            return {'success': False, 'message': f'Coupon validation failed: {str(e)}'}
    
    def apply_coupon_to_order(self, coupon_code: str, order: Order, user_id: int = None) -> Dict[str, Any]:
        """Apply coupon to order and update amounts."""
        try:
            from repositories import CouponRepository
            coupon_repo = CouponRepository()
            coupon = coupon_repo.find_by_code(coupon_code.upper())
            
            if not coupon:
                return {'success': False, 'message': 'Coupon not found'}
            
            if not coupon.can_use(user_id):
                return {'success': False, 'message': 'Coupon cannot be used'}
            
            # Calculate discount
            discount_amount = coupon.calculate_discount(order.total_amount)
            
            # Update order
            order.subtotal_amount = order.total_amount
            order.discount_amount = discount_amount
            order.coupon_code = coupon_code.upper()
            order.total_amount = order.total_amount - discount_amount
            
            # Mark coupon as used
            coupon.use_coupon()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Coupon applied! You saved ₹{discount_amount:.2f}',
                'discount_amount': discount_amount,
                'final_amount': order.total_amount
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Failed to apply coupon: {str(e)}'}


# Advanced Cart Management Methods (Session 4)
# Adding to CartService class below

def get_cart_summary_advanced(cart_service_self, user_id: int) -> Dict[str, Any]:
    """Get detailed cart summary with item breakdown."""
    try:
        cart = cart_service_self.get_user_cart(user_id)
        items = []
        
        for item in cart.items:
            items.append({
                'id': item.id,
                'product_id': item.product_id,
                'product_name': item.product_name,
                'product_image': item.product_image,
                'price': float(item.price),
                'quantity': item.quantity,
                'size': item.size,
                'subtotal': float(item.price) * item.quantity
            })
        
        return {
            'success': True,
            'cart_id': cart.id,
            'items': items,
            'item_count': cart.get_item_count(),
            'total': float(cart.get_total()),
            'created_at': cart.created_at.isoformat() if cart.created_at else None,
            'updated_at': cart.updated_at.isoformat() if cart.updated_at else None
        }
    except Exception as e:
        return {'success': False, 'message': f'Failed to get cart summary: {str(e)}'}

# Add method to CartService dynamically
CartService.get_cart_summary = get_cart_summary_advanced

def bulk_add_to_cart_advanced(cart_service_self, user_id: int, items: list) -> Dict[str, Any]:
    """Add multiple items to cart at once."""
    try:
        cart = cart_service_self.get_user_cart(user_id)
        added_count = 0
        failed_items = []
        
        for item in items:
            try:
                cart_service_self.cart_item_repo.add_item(
                    cart.id,
                    product_id=item.get('product_id'),
                    product_name=item.get('product_name'),
                    price=item.get('price'),
                    product_image=item.get('product_image'),
                    quantity=item.get('quantity', 1),
                    size=item.get('size', 'M')
                )
                added_count += 1
            except Exception as item_error:
                failed_items.append({
                    'product_id': item.get('product_id'),
                    'error': str(item_error)
                })
        
        return {
            'success': True,
            'message': f'Added {added_count} items to cart',
            'added_count': added_count,
            'failed_count': len(failed_items),
            'failed_items': failed_items,
            'cart_count': cart.get_item_count()
        }
    except Exception as e:
        return {'success': False, 'message': f'Bulk add failed: {str(e)}'}

CartService.bulk_add_to_cart = bulk_add_to_cart_advanced

def bulk_update_quantities_advanced(cart_service_self, user_id: int, updates: list) -> Dict[str, Any]:
    """Update quantities for multiple cart items at once."""
    try:
        cart = cart_service_self.get_user_cart(user_id)
        updated_count = 0
        removed_count = 0
        failed_updates = []
        
        for update in updates:
            try:
                item_id = update.get('item_id')
                quantity = update.get('quantity', 0)
                
                cart_item = cart_service_self.cart_item_repo.find_by_id(item_id)
                if not cart_item:
                    failed_updates.append({'item_id': item_id, 'error': 'Item not found'})
                    continue
                
                if quantity <= 0:
                    cart_service_self.cart_item_repo.remove_item(cart_item)
                    removed_count += 1
                else:
                    cart_service_self.cart_item_repo.update_quantity(cart_item, quantity)
                    updated_count += 1
            except Exception as update_error:
                failed_updates.append({
                    'item_id': update.get('item_id'),
                    'error': str(update_error)
                })
        
        return {
            'success': True,
            'message': f'Updated {updated_count} items, removed {removed_count}',
            'updated_count': updated_count,
            'removed_count': removed_count,
            'failed_count': len(failed_updates),
            'failed_updates': failed_updates,
            'cart_total': float(cart.get_total())
        }
    except Exception as e:
        return {'success': False, 'message': f'Batch update failed: {str(e)}'}

CartService.bulk_update_quantities = bulk_update_quantities_advanced

def check_abandoned_cart_advanced(cart_service_self, user_id: int, hours: int = 24) -> Dict[str, Any]:
    """Check if cart has been abandoned (not updated in specified hours)."""
    try:
        from datetime import datetime, timezone
        
        cart = cart_service_self.get_user_cart(user_id)
        
        if not cart.items or len(list(cart.items)) == 0:
            return {'success': True, 'is_abandoned': False, 'reason': 'Cart is empty'}
        
        hours_since_update = (datetime.now(timezone.utc) - cart.updated_at).total_seconds() / 3600
        is_abandoned = hours_since_update >= hours
        
        return {
            'success': True,
            'is_abandoned': is_abandoned,
            'hours_since_update': round(hours_since_update, 2),
            'cart_value': float(cart.get_total()),
            'item_count': cart.get_item_count(),
            'abandoned_threshold_hours': hours
        }
    except Exception as e:
        return {'success': False, 'message': f'Failed to check abandoned cart: {str(e)}'}

CartService.check_abandoned_cart = check_abandoned_cart_advanced

def merge_carts_advanced(cart_service_self, target_user_id: int, source_user_id: int) -> Dict[str, Any]:
    """Merge one user's cart into another (guest to registered user conversion)."""
    try:
        target_cart = cart_service_self.get_user_cart(target_user_id)
        source_cart = cart_service_self.get_user_cart(source_user_id)
        
        merged_count = 0
        
        for source_item in source_cart.items:
            existing_item = None
            for target_item in target_cart.items:
                if (target_item.product_id == source_item.product_id and
                    target_item.size == source_item.size):
                    existing_item = target_item
                    break
            
            if existing_item:
                cart_service_self.cart_item_repo.update_quantity(
                    existing_item,
                    existing_item.quantity + source_item.quantity
                )
            else:
                cart_service_self.cart_item_repo.add_item(
                    target_cart.id,
                    source_item.product_id,
                    source_item.product_name,
                    source_item.price,
                    source_item.product_image,
                    source_item.quantity,
                    source_item.size
                )
            merged_count += 1
        
        cart_service_self.cart_repo.clear_cart(source_cart)
        
        return {
            'success': True,
            'message': f'Merged {merged_count} items from guest cart',
            'merged_count': merged_count,
            'target_cart_total': float(target_cart.get_total())
        }
    except Exception as e:
        return {'success': False, 'message': f'Merge failed: {str(e)}'}

CartService.merge_carts = merge_carts_advanced

def get_cart_recommendations_advanced(cart_service_self, user_id: int, limit: int = 5) -> Dict[str, Any]:
    """Get personalized product recommendations based on cart items."""
    try:
        cart = cart_service_self.get_user_cart(user_id)
        
        current_product_ids = [item.product_id for item in cart.items]
        current_categories = set()
        
        for item in cart.items:
            name_lower = item.product_name.lower()
            if 'hoodie' in name_lower:
                current_categories.add('hoodie')
            elif 'tee' in name_lower or 'tshirt' in name_lower:
                current_categories.add('tee')
            elif 'model' in name_lower or 'premium' in name_lower:
                current_categories.add('premium')
            else:
                current_categories.add('general')
        
        return {
            'success': True,
            'recommendations': [],
            'categories': list(current_categories),
            'note': 'Product recommendations can be added based on cart analysis'
        }
    except Exception as e:
        return {'success': False, 'message': f'Failed to get recommendations: {str(e)}'}

CartService.get_cart_recommendations = get_cart_recommendations_advanced
