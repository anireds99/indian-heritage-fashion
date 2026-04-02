"""
Advanced Cart Management Features
Enhancements to the base CartService with bulk operations, recommendations, and analytics.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from models import Cart, CartItem, db


class AdvancedCartService:
    """Advanced cart operations including bulk operations, analytics, and recommendations."""
    
    def __init__(self, cart_service):
        """Initialize with base CartService instance."""
        self.cart_service = cart_service
        self.cart_repo = cart_service.cart_repo
        self.cart_item_repo = cart_service.cart_item_repo
    
    def get_cart_summary(self, user_id: int) -> Dict[str, Any]:
        """Get detailed cart summary with item breakdown and statistics."""
        try:
            cart = self.cart_service.get_user_cart(user_id)
            items = []
            
            for item in cart.items:
                items.append({
                    'id': item.id,
                    'product_id': item.product_id,
                    'product_name': item.product_name,
                    'product_image': item.product_image,
                    'price': item.price,
                    'quantity': item.quantity,
                    'size': item.size,
                    'subtotal': item.price * item.quantity
                })
            
            return {
                'success': True,
                'cart_id': cart.id,
                'items': items,
                'item_count': cart.get_item_count(),
                'unique_items': len(items),
                'total': cart.get_total(),
                'average_price': cart.get_total() / len(items) if items else 0,
                'created_at': cart.created_at.isoformat() if cart.created_at else None,
                'updated_at': cart.updated_at.isoformat() if cart.updated_at else None
            }
        except Exception as e:
            return {'success': False, 'message': f'Failed to get cart summary: {str(e)}'}
    
    def bulk_add_to_cart(self, user_id: int, items: List[Dict]) -> Dict[str, Any]:
        """Add multiple items to cart at once.
        
        Args:
            user_id: User ID
            items: List of dicts with product_id, quantity, size, price, product_name, product_image
        
        Returns:
            Dict with success status and added items count
        """
        try:
            cart = self.cart_service.get_user_cart(user_id)
            added_count = 0
            failed_items = []
            
            for item in items:
                try:
                    self.cart_item_repo.add_item(
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
    
    def bulk_update_quantities(self, user_id: int, updates: List[Dict]) -> Dict[str, Any]:
        """Update quantities for multiple cart items at once."""
        try:
            cart = self.cart_service.get_user_cart(user_id)
            updated_count = 0
            removed_count = 0
            failed_updates = []
            
            for update in updates:
                try:
                    item_id = update.get('item_id')
                    quantity = update.get('quantity', 0)
                    
                    cart_item = self.cart_item_repo.find_by_id(item_id)
                    if not cart_item:
                        failed_updates.append({'item_id': item_id, 'error': 'Item not found'})
                        continue
                    
                    if quantity <= 0:
                        self.cart_item_repo.remove_item(cart_item)
                        removed_count += 1
                    else:
                        self.cart_item_repo.update_quantity(cart_item, quantity)
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
                'cart_total': cart.get_total()
            }
        except Exception as e:
            return {'success': False, 'message': f'Batch update failed: {str(e)}'}
    
    def check_abandoned_cart(self, user_id: int, hours: int = 24) -> Dict[str, Any]:
        """Check if cart has been abandoned (not updated in specified hours)."""
        try:
            cart = self.cart_service.get_user_cart(user_id)
            
            if not cart.items.count():
                return {'success': True, 'is_abandoned': False, 'reason': 'Cart is empty'}
            
            hours_since_update = (datetime.now(timezone.utc) - cart.updated_at).total_seconds() / 3600
            is_abandoned = hours_since_update >= hours
            
            return {
                'success': True,
                'is_abandoned': is_abandoned,
                'hours_since_update': round(hours_since_update, 2),
                'cart_value': cart.get_total(),
                'item_count': cart.get_item_count(),
                'abandoned_threshold_hours': hours
            }
        except Exception as e:
            return {'success': False, 'message': f'Failed to check abandoned cart: {str(e)}'}
    
    def merge_carts(self, target_user_id: int, source_user_id: int) -> Dict[str, Any]:
        """Merge one user's cart into another (guest to registered user conversion)."""
        try:
            target_cart = self.cart_service.get_user_cart(target_user_id)
            source_cart = self.cart_service.get_user_cart(source_user_id)
            
            merged_count = 0
            
            for source_item in source_cart.items:
                # Check if item already in target cart
                existing_item = None
                for target_item in target_cart.items:
                    if (target_item.product_id == source_item.product_id and
                        target_item.size == source_item.size):
                        existing_item = target_item
                        break
                
                if existing_item:
                    # Merge quantities
                    self.cart_item_repo.update_quantity(
                        existing_item,
                        existing_item.quantity + source_item.quantity
                    )
                else:
                    # Add as new item
                    self.cart_item_repo.add_item(
                        target_cart.id,
                        source_item.product_id,
                        source_item.product_name,
                        source_item.price,
                        source_item.product_image,
                        source_item.quantity,
                        source_item.size
                    )
                merged_count += 1
            
            # Clear source cart
            self.cart_repo.clear_cart(source_cart)
            
            return {
                'success': True,
                'message': f'Merged {merged_count} items from guest cart',
                'merged_count': merged_count,
                'target_cart_total': target_cart.get_total()
            }
        except Exception as e:
            return {'success': False, 'message': f'Merge failed: {str(e)}'}
    
    def get_cart_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get detailed analytics about cart contents."""
        try:
            cart = self.cart_service.get_user_cart(user_id)
            
            if not cart.items:
                return {
                    'success': True,
                    'item_count': 0,
                    'total_quantity': 0,
                    'total_value': 0,
                    'average_item_price': 0,
                    'size_distribution': {},
                    'product_categories': {}
                }
            
            # Calculate statistics
            total_quantity = sum(item.quantity for item in cart.items)
            total_value = cart.get_total()
            avg_price = total_value / len(cart.items)
            
            # Size distribution
            size_dist = {}
            for item in cart.items:
                size_dist[item.size] = size_dist.get(item.size, 0) + item.quantity
            
            # Extract categories from product names
            categories = {}
            for item in cart.items:
                name_lower = item.product_name.lower()
                if 'hoodie' in name_lower:
                    cat = 'Hoodies'
                elif 'tee' in name_lower or 'tshirt' in name_lower:
                    cat = 'T-Shirts'
                elif 'model' in name_lower or 'premium' in name_lower:
                    cat = 'Premium'
                else:
                    cat = 'Other'
                categories[cat] = categories.get(cat, 0) + item.quantity
            
            return {
                'success': True,
                'item_count': len(cart.items),
                'total_quantity': total_quantity,
                'total_value': round(total_value, 2),
                'average_item_price': round(avg_price, 2),
                'size_distribution': size_dist,
                'product_categories': categories,
                'most_expensive_item': max((item.price for item in cart.items), default=0),
                'least_expensive_item': min((item.price for item in cart.items), default=0)
            }
        except Exception as e:
            return {'success': False, 'message': f'Failed to get cart analytics: {str(e)}'}
    
    def validate_cart_stock(self, user_id: int, stock_data: Dict[int, int]) -> Dict[str, Any]:
        """Validate cart items against available stock.
        
        Args:
            user_id: User ID
            stock_data: Dict mapping product_id to available quantity
        
        Returns:
            Dict with validation results
        """
        try:
            cart = self.cart_service.get_user_cart(user_id)
            out_of_stock = []
            low_stock = []
            valid_items = []
            
            for item in cart.items:
                available = stock_data.get(item.product_id, 0)
                
                if available <= 0:
                    out_of_stock.append({
                        'product_id': item.product_id,
                        'product_name': item.product_name,
                        'requested': item.quantity,
                        'available': 0
                    })
                elif available < item.quantity:
                    low_stock.append({
                        'product_id': item.product_id,
                        'product_name': item.product_name,
                        'requested': item.quantity,
                        'available': available
                    })
                    valid_items.append(item.product_id)
                else:
                    valid_items.append(item.product_id)
            
            is_valid = len(out_of_stock) == 0
            
            return {
                'success': True,
                'is_valid': is_valid,
                'valid_items': valid_items,
                'out_of_stock': out_of_stock,
                'low_stock': low_stock,
                'can_checkout': is_valid
            }
        except Exception as e:
            return {'success': False, 'message': f'Failed to validate cart stock: {str(e)}'}
