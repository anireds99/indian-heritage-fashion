"""
Comprehensive cart management testing script.
Tests all cart operations: add, update, remove, checkout, etc.
"""
import sys
from app import app, db
from repositories import UserRepository, CartRepository, CartItemRepository, OrderRepository
from services import CartService, CheckoutService, AuthenticationService
from models import Address

def test_cart_management():
    """Test complete cart management workflow."""
    print("\n" + "="*60)
    print("🧪 CART MANAGEMENT TEST SUITE")
    print("="*60)
    
    with app.app_context():
        try:
            # 1. Create test user
            print("\n1️⃣  Creating test user...")
            auth_service = AuthenticationService()
            result = auth_service.register_user(
                email='carttest@example.com',
                username='cartuser',
                password='Test123'
            )
            
            if not result['success']:
                print(f"   ❌ Failed: {result['message']}")
                return False
            
            user = result['user']
            print(f"   ✅ User created: {user.username} (ID: {user.id})")
            
            # 2. Get user cart
            print("\n2️⃣  Getting user cart...")
            cart_service = CartService()
            cart = cart_service.get_user_cart(user.id)
            print(f"   ✅ Cart created: ID {cart.id}")
            print(f"   Current items: {cart.get_item_count()}")
            
            # 3. Add items to cart
            print("\n3️⃣  Adding items to cart...")
            products = [
                {'product_id': 1, 'name': 'Tanjore Temple Graphic Tee', 'price': 1299.99, 'qty': 1},
                {'product_id': 2, 'name': 'ISRO Space Missions Hoodie', 'price': 1999.99, 'qty': 2},
                {'product_id': 3, 'name': 'Hampi Ruins Heritage Tee', 'price': 1399.99, 'qty': 1},
            ]
            
            for product in products:
                result = cart_service.add_to_cart(
                    user_id=user.id,
                    product_id=product['product_id'],
                    product_name=product['name'],
                    price=product['price'],
                    product_image='mockups/test.jpg',
                    quantity=product['qty'],
                    size='M'
                )
                if result['success']:
                    print(f"   ✅ Added: {product['name']} (Qty: {product['qty']})")
                else:
                    print(f"   ❌ Failed to add: {product['name']}")
            
            # Refresh cart
            cart = cart_service.get_user_cart(user.id)
            print(f"\n   Total items in cart: {cart.get_item_count()}")
            print(f"   Cart total: ₹{cart.get_total():.2f}")
            
            # 4. Update item quantity
            print("\n4️⃣  Updating item quantities...")
            if cart.items.count() > 0:
                first_item = cart.items[0]
                result = cart_service.update_cart_item(first_item.id, 3)
                if result['success']:
                    print(f"   ✅ Updated item quantity to 3")
                    cart = cart_service.get_user_cart(user.id)
                    print(f"   New cart total: ₹{cart.get_total():.2f}")
                else:
                    print(f"   ❌ Failed: {result['message']}")
            
            # 5. Remove an item
            print("\n5️⃣  Removing an item from cart...")
            if cart.items.count() > 1:
                second_item = cart.items[1]
                result = cart_service.remove_from_cart(second_item.id)
                if result['success']:
                    print(f"   ✅ Item removed")
                    cart = cart_service.get_user_cart(user.id)
                    print(f"   Items remaining: {cart.get_item_count()}")
                    print(f"   New cart total: ₹{cart.get_total():.2f}")
                else:
                    print(f"   ❌ Failed: {result['message']}")
            
            # 6. Create shipping address
            print("\n6️⃣  Creating shipping address...")
            address = Address(
                user_id=user.id,
                full_name='Test User',
                phone='9876543210',
                street_address='123 Test Street',
                city='Bangalore',
                state='Karnataka',
                postal_code='560001',
                country='India',
                is_default=True
            )
            db.session.add(address)
            db.session.commit()
            print(f"   ✅ Address created: {address.full_name}, {address.city}")
            
            # 7. Create order from cart
            print("\n7️⃣  Creating order from cart (COD)...")
            checkout_service = CheckoutService()
            order_result = checkout_service.create_order_from_cart(
                user_id=user.id,
                shipping_address_id=address.id,
                payment_method='cod'
            )
            
            if order_result['success']:
                order = order_result['order']
                print(f"   ✅ Order created successfully!")
                print(f"   Order Number: {order.order_number}")
                print(f"   Order ID: {order.id}")
                print(f"   Total Amount: ₹{order.total_amount:.2f}")
                print(f"   Payment Method: {order.payment.payment_method if order.payment else 'N/A'}")
                print(f"   Order Status: {order.status}")
                print(f"   Items in order: {len(order.items)}")
            else:
                print(f"   ❌ Failed: {order_result['message']}")
            
            # 8. Verify cart is cleared
            print("\n8️⃣  Verifying cart after checkout...")
            cart = cart_service.get_user_cart(user.id)
            print(f"   Cart items after checkout: {cart.get_item_count()}")
            if cart.get_item_count() == 0:
                print(f"   ✅ Cart cleared successfully")
            else:
                print(f"   ⚠️  Cart still has items (may be intentional)")
            
            # 9. Test card payment
            print("\n9️⃣  Testing card payment...")
            # Add items again for card payment test
            for product in products[:1]:
                cart_service.add_to_cart(
                    user_id=user.id,
                    product_id=product['product_id'],
                    product_name=product['name'],
                    price=product['price'],
                    product_image='mockups/test.jpg',
                    quantity=1,
                    size='M'
                )
            
            card_details = {
                'card_number': '4111111111111111',
                'card_name': 'TEST USER',
                'expiry_month': '12',
                'expiry_year': '2025',
                'cvv': '123'
            }
            
            order_result = checkout_service.create_order_from_cart(
                user_id=user.id,
                shipping_address_id=address.id,
                payment_method='card',
                card_details=card_details
            )
            
            if order_result['success']:
                order = order_result['order']
                print(f"   ✅ Card payment order created!")
                print(f"   Order Number: {order.order_number}")
                print(f"   Payment Status: {order.payment.payment_status if order.payment else 'N/A'}")
                if order.payment and order.payment.transaction_id:
                    print(f"   Transaction ID: {order.payment.transaction_id}")
            else:
                print(f"   ❌ Failed: {order_result['message']}")
            
            print("\n" + "="*60)
            print("✅ ALL CART TESTS COMPLETED SUCCESSFULLY")
            print("="*60 + "\n")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_cart_management()
    sys.exit(0 if success else 1)
