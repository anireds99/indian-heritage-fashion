"""
Comprehensive test suite for cart management enhancements.
Tests: bulk operations, recommendations, abandoned cart detection, cart merging.
"""
from datetime import datetime, timezone
from app import app, db

# Test cart summary functionality
def test_cart_summary():
    """Test getting detailed cart summary."""
    print("\n=== Testing Cart Summary ===")
    try:
        with app.app_context():
            from services import CartService, AuthenticationService
            
            cart_service = CartService()
            auth_service = AuthenticationService()
            
            # Create test user
            result = auth_service.register_user(
                email=f"cart_test_{datetime.now().timestamp()}@test.com",
                username=f"cartuser_{int(datetime.now().timestamp())}",
                password="Test@123456"
            )
            
            if not result['success']:
                print(f"❌ Failed to create test user: {result['message']}")
                return
            
            user_id = result['user'].id
            print(f"✅ Created test user: {user_id}")
            
            # Add items to cart using bulk operation
            items_to_add = [
                {
                    'product_id': 1,
                    'product_name': 'Tanjore Temple Graphic Tee',
                    'price': 1299.99,
                    'product_image': 'mockups/tanjore.jpg',
                    'quantity': 2,
                    'size': 'M'
                },
                {
                    'product_id': 2,
                    'product_name': 'ISRO Space Missions Hoodie',
                    'price': 1999.99,
                    'product_image': 'mockups/isro_1st_rocket.jpg',
                    'quantity': 1,
                    'size': 'L'
                }
            ]
            
            bulk_result = cart_service.bulk_add_to_cart(user_id, items_to_add)
            print(f"✅ Bulk add result: {bulk_result['message']}")
            print(f"   - Added: {bulk_result['added_count']}")
            print(f"   - Failed: {bulk_result['failed_count']}")
            print(f"   - Cart count: {bulk_result['cart_count']}")
            
            # Get cart summary
            summary = cart_service.get_cart_summary(user_id)
            if summary['success']:
                print(f"✅ Cart Summary:")
                print(f"   - Item count: {summary['item_count']}")
                print(f"   - Total: ₹{summary['total']:.2f}")
                for item in summary['items']:
                    print(f"     • {item['product_name']}: {item['quantity']} x ₹{item['price']:.2f}")
            else:
                print(f"❌ Failed to get cart summary: {summary['message']}")
    
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

# Test bulk update quantities
def test_bulk_update():
    """Test updating multiple cart items at once."""
    print("\n=== Testing Bulk Update Quantities ===")
    try:
        with app.app_context():
            from services import CartService, AuthenticationService
            
            cart_service = CartService()
            auth_service = AuthenticationService()
            
            # Create test user
            result = auth_service.register_user(
                email=f"bulk_test_{datetime.now().timestamp()}@test.com",
                username=f"bulkuser_{int(datetime.now().timestamp())}",
                password="Test@123456"
            )
            
            if not result['success']:
                print(f"❌ Failed to create test user: {result['message']}")
                return
            
            user_id = result['user'].id
            print(f"✅ Created test user: {user_id}")
            
            # Add items to cart
            cart_service.add_to_cart(user_id, 1, 'Tanjore Temple Graphic Tee', 1299.99, 'mockups/tanjore.jpg', 2, 'M')
            cart_service.add_to_cart(user_id, 2, 'ISRO Space Missions Hoodie', 1999.99, 'mockups/isro_1st_rocket.jpg', 1, 'L')
            
            # Get cart items
            cart = cart_service.get_user_cart(user_id)
            items = list(cart.items)
            
            if len(items) < 2:
                print(f"❌ Not enough items in cart to test bulk update")
                return
            
            # Prepare updates
            updates = [
                {'item_id': items[0].id, 'quantity': 5},
                {'item_id': items[1].id, 'quantity': 3}
            ]
            
            # Perform bulk update
            update_result = cart_service.bulk_update_quantities(user_id, updates)
            print(f"✅ Bulk update result: {update_result['message']}")
            print(f"   - Updated: {update_result['updated_count']}")
            print(f"   - Removed: {update_result['removed_count']}")
            print(f"   - Cart total: ₹{update_result['cart_total']:.2f}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

# Test abandoned cart detection
def test_abandoned_cart():
    """Test detecting abandoned carts."""
    print("\n=== Testing Abandoned Cart Detection ===")
    try:
        with app.app_context():
            from services import CartService, AuthenticationService
            
            cart_service = CartService()
            auth_service = AuthenticationService()
            
            # Create test user
            result = auth_service.register_user(
                email=f"abandoned_test_{datetime.now().timestamp()}@test.com",
                username=f"abandoneduser_{int(datetime.now().timestamp())}",
                password="Test@123456"
            )
            
            if not result['success']:
                print(f"❌ Failed to create test user: {result['message']}")
                return
            
            user_id = result['user'].id
            print(f"✅ Created test user: {user_id}")
            
            # Add item to cart
            cart_service.add_to_cart(user_id, 1, 'Tanjore Temple Graphic Tee', 1299.99, 'mockups/tanjore.jpg', 1, 'M')
            
            # Check if cart is abandoned
            abandoned_check = cart_service.check_abandoned_cart(user_id, hours=24)
            print(f"✅ Abandoned cart check (24 hours threshold):")
            print(f"   - Is abandoned: {abandoned_check['is_abandoned']}")
            print(f"   - Hours since update: {abandoned_check['hours_since_update']}")
            print(f"   - Cart value: ₹{abandoned_check['cart_value']:.2f}")
            print(f"   - Item count: {abandoned_check['item_count']}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

# Test cart merge functionality
def test_cart_merge():
    """Test merging carts from guest to registered user."""
    print("\n=== Testing Cart Merge (Guest to Registered User) ===")
    try:
        with app.app_context():
            from services import CartService, AuthenticationService
            
            cart_service = CartService()
            auth_service = AuthenticationService()
            
            # Create guest user
            guest_result = auth_service.register_user(
                email=f"guest_{datetime.now().timestamp()}@test.com",
                username=f"guestuser_{int(datetime.now().timestamp())}",
                password="Test@123456"
            )
            
            if not guest_result['success']:
                print(f"❌ Failed to create guest user: {guest_result['message']}")
                return
            
            guest_id = guest_result['user'].id
            print(f"✅ Created guest user: {guest_id}")
            
            # Create registered user
            registered_result = auth_service.register_user(
                email=f"registered_{datetime.now().timestamp()}@test.com",
                username=f"registereduser_{int(datetime.now().timestamp())}",
                password="Test@123456"
            )
            
            if not registered_result['success']:
                print(f"❌ Failed to create registered user: {registered_result['message']}")
                return
            
            registered_id = registered_result['user'].id
            print(f"✅ Created registered user: {registered_id}")
            
            # Add items to guest cart
            cart_service.add_to_cart(guest_id, 1, 'Tanjore Temple Graphic Tee', 1299.99, 'mockups/tanjore.jpg', 2, 'M')
            cart_service.add_to_cart(guest_id, 2, 'ISRO Space Missions Hoodie', 1999.99, 'mockups/isro_1st_rocket.jpg', 1, 'L')
            
            # Add items to registered cart
            cart_service.add_to_cart(registered_id, 3, 'Hampi Ruins Heritage Tee', 1399.99, 'mockups/hampi_temple_tshirt.jpg', 1, 'S')
            
            # Merge carts
            merge_result = cart_service.merge_carts(registered_id, guest_id)
            print(f"✅ Cart merge result: {merge_result['message']}")
            print(f"   - Merged items: {merge_result['merged_count']}")
            print(f"   - Target cart total: ₹{merge_result['target_cart_total']:.2f}")
            
            # Verify registered cart has all items
            registered_summary = cart_service.get_cart_summary(registered_id)
            if registered_summary['success']:
                print(f"✅ Registered user cart after merge:")
                print(f"   - Total items: {registered_summary['item_count']}")
                print(f"   - Cart total: ₹{registered_summary['total']:.2f}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

# Test cart recommendations
def test_recommendations():
    """Test getting cart-based product recommendations."""
    print("\n=== Testing Cart Recommendations ===")
    try:
        with app.app_context():
            from services import CartService, AuthenticationService
            
            cart_service = CartService()
            auth_service = AuthenticationService()
            
            # Create test user
            result = auth_service.register_user(
                email=f"recommendations_{datetime.now().timestamp()}@test.com",
                username=f"recommenduser_{int(datetime.now().timestamp())}",
                password="Test@123456"
            )
            
            if not result['success']:
                print(f"❌ Failed to create test user: {result['message']}")
                return
            
            user_id = result['user'].id
            print(f"✅ Created test user: {user_id}")
            
            # Add items to cart
            cart_service.add_to_cart(user_id, 1, 'Tanjore Temple Graphic Tee', 1299.99, 'mockups/tanjore.jpg', 1, 'M')
            cart_service.add_to_cart(user_id, 2, 'ISRO Space Missions Hoodie', 1999.99, 'mockups/isro_1st_rocket.jpg', 1, 'L')
            
            # Get recommendations
            recommendations = cart_service.get_cart_recommendations(user_id, limit=5)
            print(f"✅ Cart recommendations:")
            print(f"   - Categories: {recommendations['categories']}")
            print(f"   - Recommendations count: {len(recommendations['recommendations'])}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == '__main__':
    print("=" * 60)
    print("CART MANAGEMENT ENHANCEMENTS - TEST SUITE")
    print("=" * 60)
    
    test_cart_summary()
    test_bulk_update()
    test_abandoned_cart()
    test_cart_merge()
    test_recommendations()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)
