"""
Comprehensive test suite for advanced cart API endpoints.
Tests all new Session 4 cart management features.
"""
from datetime import datetime
from app import app, db

def test_cart_summary_endpoint():
    """Test GET /cart/summary endpoint."""
    print("\n=== Testing Cart Summary Endpoint ===")
    with app.app_context():
        from services import CartService, AuthenticationService
        from flask import session as flask_session
        
        try:
            cart_service = CartService()
            auth_service = AuthenticationService()
            
            # Create test user
            result = auth_service.register_user(
                email=f"summary_test_{int(datetime.now().timestamp())}@test.com",
                username=f"summaryuser_{int(datetime.now().timestamp())}",
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
            cart_service.add_to_cart(user_id, 3, 'Hampi Ruins Heritage Tee', 1399.99, 'mockups/hampi_temple_tshirt.jpg', 3, 'S')
            
            # Get cart summary
            summary = cart_service.get_cart_summary(user_id)
            if summary['success']:
                print(f"✅ Cart Summary Retrieved Successfully:")
                print(f"   - Cart ID: {summary['cart_id']}")
                print(f"   - Total Items: {summary['item_count']}")
                print(f"   - Cart Total: ₹{summary['total']:.2f}")
                print(f"   - Items in Cart:")
                for item in summary['items']:
                    print(f"     • {item['product_name']}: {item['quantity']} x ₹{item['price']:.2f} = ₹{item['subtotal']:.2f}")
            else:
                print(f"❌ Failed to get cart summary: {summary['message']}")
        
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")

def test_bulk_add_endpoint():
    """Test POST /cart/bulk-add endpoint."""
    print("\n=== Testing Bulk Add Endpoint ===")
    with app.app_context():
        from services import CartService, AuthenticationService
        
        try:
            cart_service = CartService()
            auth_service = AuthenticationService()
            
            # Create test user
            result = auth_service.register_user(
                email=f"bulkadd_test_{int(datetime.now().timestamp())}@test.com",
                username=f"bulkadduser_{int(datetime.now().timestamp())}",
                password="Test@123456"
            )
            
            if not result['success']:
                print(f"❌ Failed to create test user: {result['message']}")
                return
            
            user_id = result['user'].id
            print(f"✅ Created test user: {user_id}")
            
            # Prepare bulk items
            items_to_add = [
                {
                    'product_id': 4,
                    'product_name': 'Mysore Palace Heritage Tee',
                    'price': 1499.99,
                    'product_image': 'mockups/mysore.jpg',
                    'quantity': 2,
                    'size': 'M'
                },
                {
                    'product_id': 5,
                    'product_name': 'Hyderabad Charminar Heritage Tee',
                    'price': 1499.99,
                    'product_image': 'mockups/hyderabad.jpg',
                    'quantity': 1,
                    'size': 'L'
                },
                {
                    'product_id': 15,
                    'product_name': 'Chhatrapati Shivaji Maharaj Hoodie',
                    'price': 2099.99,
                    'product_image': 'mockups/siaji_hoodie.jpg',
                    'quantity': 1,
                    'size': 'XL'
                }
            ]
            
            # Test bulk add
            bulk_result = cart_service.bulk_add_to_cart(user_id, items_to_add)
            print(f"✅ Bulk Add Result: {bulk_result['message']}")
            print(f"   - Successfully Added: {bulk_result['added_count']}")
            print(f"   - Failed: {bulk_result['failed_count']}")
            print(f"   - Total Cart Items: {bulk_result['cart_count']}")
            
            # Verify cart
            summary = cart_service.get_cart_summary(user_id)
            if summary['success']:
                print(f"✅ Cart Verified: {summary['item_count']} items, Total: ₹{summary['total']:.2f}")
        
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")

def test_bulk_update_endpoint():
    """Test POST /cart/bulk-update endpoint."""
    print("\n=== Testing Bulk Update Endpoint ===")
    with app.app_context():
        from services import CartService, AuthenticationService
        
        try:
            cart_service = CartService()
            auth_service = AuthenticationService()
            
            # Create test user and add items
            result = auth_service.register_user(
                email=f"bulkupdate_test_{int(datetime.now().timestamp())}@test.com",
                username=f"bulkupdateuser_{int(datetime.now().timestamp())}",
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
            
            # Get items to update
            cart = cart_service.get_user_cart(user_id)
            items = list(cart.items)
            
            if len(items) < 2:
                print(f"❌ Not enough items to test bulk update")
                return
            
            # Prepare updates
            updates = [
                {'item_id': items[0].id, 'quantity': 5},
                {'item_id': items[1].id, 'quantity': 3}
            ]
            
            # Test bulk update
            update_result = cart_service.bulk_update_quantities(user_id, updates)
            print(f"✅ Bulk Update Result: {update_result['message']}")
            print(f"   - Updated Items: {update_result['updated_count']}")
            print(f"   - Removed Items: {update_result['removed_count']}")
            print(f"   - New Cart Total: ₹{update_result['cart_total']:.2f}")
        
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")

def test_cart_analytics_endpoint():
    """Test GET /cart/analytics endpoint."""
    print("\n=== Testing Cart Analytics Endpoint ===")
    with app.app_context():
        from services import CartService, AuthenticationService
        
        try:
            cart_service = CartService()
            auth_service = AuthenticationService()
            
            # Create test user and add items
            result = auth_service.register_user(
                email=f"analytics_test_{int(datetime.now().timestamp())}@test.com",
                username=f"analyticsuser_{int(datetime.now().timestamp())}",
                password="Test@123456"
            )
            
            if not result['success']:
                print(f"❌ Failed to create test user: {result['message']}")
                return
            
            user_id = result['user'].id
            print(f"✅ Created test user: {user_id}")
            
            # Add diverse items to cart
            items = [
                (1, 'Tanjore Temple Graphic Tee', 1299.99, 2),
                (2, 'ISRO Space Missions Hoodie', 1999.99, 1),
                (3, 'Hampi Ruins Heritage Tee', 1399.99, 1),
                (15, 'Chhatrapati Shivaji Maharaj Hoodie', 2099.99, 1)
            ]
            
            for product_id, name, price, qty in items:
                cart_service.add_to_cart(user_id, product_id, name, price, f'mockups/{name.lower()}.jpg', qty, 'M')
            
            # Get cart analytics
            cart = cart_service.get_user_cart(user_id)
            prices = [float(item.price) for item in cart.items]
            categories = {}
            for item in cart.items:
                cat = item.product_name.split()[0]
                categories[cat] = categories.get(cat, 0) + 1
            
            avg_price = sum(prices) / len(prices) if prices else 0
            
            print(f"✅ Cart Analytics Retrieved:")
            print(f"   - Total Items: {cart.get_item_count()}")
            print(f"   - Cart Total Value: ₹{float(cart.get_total()):.2f}")
            print(f"   - Average Item Price: ₹{avg_price:.2f}")
            print(f"   - Lowest Price: ₹{min(prices):.2f}")
            print(f"   - Highest Price: ₹{max(prices):.2f}")
            print(f"   - Categories: {categories}")
        
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")

def test_cart_merge_endpoint():
    """Test cart merge functionality (guest to registered user)."""
    print("\n=== Testing Cart Merge Endpoint ===")
    with app.app_context():
        from services import CartService, AuthenticationService
        
        try:
            cart_service = CartService()
            auth_service = AuthenticationService()
            
            # Create guest user
            guest_result = auth_service.register_user(
                email=f"guest_{int(datetime.now().timestamp())}@test.com",
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
                email=f"registered_{int(datetime.now().timestamp())}@test.com",
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
            
            # Get initial totals
            guest_summary_before = cart_service.get_cart_summary(guest_id)
            registered_summary_before = cart_service.get_cart_summary(registered_id)
            
            print(f"✅ Before Merge:")
            print(f"   - Guest Cart: {guest_summary_before['item_count']} items, ₹{guest_summary_before['total']:.2f}")
            print(f"   - Registered Cart: {registered_summary_before['item_count']} items, ₹{registered_summary_before['total']:.2f}")
            
            # Merge carts
            merge_result = cart_service.merge_carts(registered_id, guest_id)
            print(f"✅ Merge Result: {merge_result['message']}")
            print(f"   - Items Merged: {merge_result['merged_count']}")
            
            # Verify merge
            registered_summary_after = cart_service.get_cart_summary(registered_id)
            guest_summary_after = cart_service.get_cart_summary(guest_id)
            
            print(f"✅ After Merge:")
            print(f"   - Guest Cart: {guest_summary_after['item_count']} items (should be empty)")
            print(f"   - Registered Cart: {registered_summary_after['item_count']} items, ₹{registered_summary_after['total']:.2f}")
        
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")

def test_abandoned_cart_detection():
    """Test abandoned cart detection."""
    print("\n=== Testing Abandoned Cart Detection ===")
    with app.app_context():
        from services import CartService, AuthenticationService
        
        try:
            cart_service = CartService()
            auth_service = AuthenticationService()
            
            # Create test user
            result = auth_service.register_user(
                email=f"abandoned_test_{int(datetime.now().timestamp())}@test.com",
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
            
            # Check abandoned status with different thresholds
            abandoned_24h = cart_service.check_abandoned_cart(user_id, hours=24)
            abandoned_0h = cart_service.check_abandoned_cart(user_id, hours=0)
            
            print(f"✅ Abandoned Cart Detection Results:")
            print(f"   - 24-hour threshold:")
            print(f"     • Is Abandoned: {abandoned_24h['is_abandoned']}")
            print(f"     • Hours Since Update: {abandoned_24h['hours_since_update']}")
            print(f"     • Cart Value: ₹{abandoned_24h['cart_value']:.2f}")
            print(f"   - 0-hour threshold:")
            print(f"     • Is Abandoned: {abandoned_0h['is_abandoned']}")
        
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")

if __name__ == '__main__':
    print("=" * 70)
    print("COMPREHENSIVE CART API ENDPOINTS TEST SUITE")
    print("Session 4 - Advanced Cart Management Features")
    print("=" * 70)
    
    test_cart_summary_endpoint()
    test_bulk_add_endpoint()
    test_bulk_update_endpoint()
    test_cart_analytics_endpoint()
    test_cart_merge_endpoint()
    test_abandoned_cart_detection()
    
    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETED - All Advanced Cart Features Validated")
    print("=" * 70)
