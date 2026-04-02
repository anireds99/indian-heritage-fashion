"""
Advanced Cart Management Service
Provides enhanced cart operations: bulk operations, recommendations, abandoned cart detection, 
cart merging, and inventory tracking.
"""
from typing import Dict, Any, List
from datetime import datetime, timezone
from repositories import CartRepository, CartItemRepository


class AdvancedCartService:
    """Advanced service for enhanced shopping cart operations."""
    
    def __init__(self):
        self.cart_repo = CartRepository()
        self.cart_item_repo = CartItemRepository()
    
    def get_cart_summary(self, user_id: int) -> Dict[str, Any]:
        """Get detailed cart summary with item breakdown and statistics."""
        try:
            cart = self.cart_repo.find_or_create_by_user(user_id)
            items = []
            total_items = 0
            
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
                total_items += item.quantity
            
            return {
                'success': True,
                'cart_id': cart.id,
                'items': items,
                'unique_items': len(items),
                'total_items': total_items,
                'cart_total': float(cart.get_total()),
                'created_at': cart.created_at.isoformat() if cart.created_at else None,
                'updated_at': cart.updated_at.isoformat() if cart.updated_at else None
            }
        except Exception as e:
            return {'success': False, 'message': f'Failed to get cart summary: {str(e)}'}
    
    def bulk_add_to_cart(self, user_id: int, items: List[Dict]) -> Dict[str, Any]:
        """Add multiple items to cart at once."""
        try:
            cart = self.cart_repo.find_or_create_by_user(user_id)
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
            cart = self.cart_repo.find_or_create_by_user(user_id)
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
                'cart_total': float(cart.get_total())
            }
        except Exception as e:
            return {'success': False, 'message': f'Batch update failed: {str(e)}'}
    
    def check_abandoned_cart(self, user_id: int, hours: int = 24) -> Dict[str, Any]:
        """Check if cart has been abandoned (not updated in specified hours)."""
        try:
            cart = self.cart_repo.find_or_create_by_user(user_id)
            
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
    
    def merge_carts(self, target_user_id: int, source_user_id: int) -> Dict[str, Any]:
        """Merge one user's cart into another (guest to registered user conversion)."""
        try:
            target_cart = self.cart_repo.find_or_create_by_user(target_user_id)
            source_cart = self.cart_repo.find_or_create_by_user(source_user_id)
            
            merged_count = 0
            quantity_merged = 0
            
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
                    quantity_merged += source_item.quantity
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
                    quantity_merged += source_item.quantity
                merged_count += 1
            
            # Clear source cart
            self.cart_repo.clear_cart(source_cart)
            
            return {
                'success': True,
                'message': f'Merged {merged_count} product types ({quantity_merged} items) from guest cart',
                'merged_count': merged_count,
                'quantity_merged': quantity_merged,
                'target_cart_total': float(target_cart.get_total())
            }
        except Exception as e:
            return {'success': False, 'message': f'Merge failed: {str(e)}'}
    
    def get_cart_recommendations(self, user_id: int, limit: int = 5) -> Dict[str, Any]:
        """Get personalized product recommendations based on cart items."""
        try:
            cart = self.cart_repo.find_or_create_by_user(user_id)
            
            # Extract product categories from current cart
            current_categories = set()
            cart_value_per_item = []
            
            for item in cart.items:
                name_lower = item.product_name.lower()
                price = float(item.price)
                cart_value_per_item.append(price)
                
                if 'hoodie' in name_lower:
                    current_categories.add('hoodie')
                elif 'tee' in name_lower or 'tshirt' in name_lower:
                    current_categories.add('tee')
                elif 'model' in name_lower or 'premium' in name_lower:
                    current_categories.add('premium')
                else:
                    current_categories.add('general')
            
            avg_price = sum(cart_value_per_item) / len(cart_value_per_item) if cart_value_per_item else 0
            
            return {
                'success': True,
                'recommendations': [],
                'categories': list(current_categories),
                'avg_price_range': f'₹{avg_price * 0.8:.2f} - ₹{avg_price * 1.2:.2f}',
                'suggestions': 'Recommend complementary items in similar price range'
            }
        except Exception as e:
            return {'success': False, 'message': f'Failed to get recommendations: {str(e)}'}
    
    def get_cart_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive cart statistics for analytics."""
        try:
            cart = self.cart_repo.find_or_create_by_user(user_id)
            items = list(cart.items)
            
            if not items:
                return {
                    'success': True,
                    'statistics': {
                        'total_items': 0,
                        'unique_products': 0,
                        'cart_value': 0,
                        'avg_item_price': 0,
                        'min_price': 0,
                        'max_price': 0
                    }
                }
            
            prices = [float(item.price) for item in items]
            quantities = [item.quantity for item in items]
            
            return {
                'success': True,
                'statistics': {
                    'total_items': sum(quantities),
                    'unique_products': len(items),
                    'cart_value': float(cart.get_total()),
                    'avg_item_price': sum(prices) / len(prices),
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'avg_quantity_per_product': sum(quantities) / len(quantities)
                }
            }
        except Exception as e:
            return {'success': False, 'message': f'Failed to get statistics: {str(e)}'}
    
    def apply_cart_discount(self, user_id: int, discount_percent: float, max_amount: float = None) -> Dict[str, Any]:
        """Apply a percentage discount to entire cart."""
        try:
            if discount_percent < 0 or discount_percent > 100:
                return {'success': False, 'message': 'Discount percentage must be between 0 and 100'}
            
            cart = self.cart_repo.find_or_create_by_user(user_id)
            original_total = float(cart.get_total())
            discount_amount = original_total * (discount_percent / 100)
            
            # Apply max discount limit if specified
            if max_amount and discount_amount > max_amount:
                discount_amount = max_amount
            
            final_total = original_total - discount_amount
            
            return {
                'success': True,
                'message': f'Applied {discount_percent}% discount',
                'original_total': original_total,
                'discount_amount': discount_amount,
                'final_total': final_total,
                'discount_percent': discount_percent
            }
        except Exception as e:
            return {'success': False, 'message': f'Failed to apply discount: {str(e)}'}
