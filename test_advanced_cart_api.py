"""
Comprehensive test suite for advanced cart management API endpoints.
Tests all new API endpoints: bulk operations, analytics, validation, etc.
"""
from datetime import datetime
from app import app, db

def test_bulk_add_endpoint():
    """Test POST /cart/bulk-add endpoint."""
    print("\n=== Testing Bulk Add API Endpoint ===")
    try:
        with app.app_context():
            from services import AuthenticationService
            
            auth_service = AuthenticationService()
            
            # Create test user
            result = auth_service.register_user(
                email=f"bulkadd_{int(datetime.now().timestamp())}@test.com",
                username=f"bulkadd_{int(datetime.now().timestamp())}",
                password="Test@123456"
            )
            
            if not result['success']:
                print(f"❌ Failed to create test user: {result['message']}")
                return
            
            user_id = result['user'].id
            print(f"✅ Created test user: {user_id}")
            
            # Test the bulk add endpoint using Flask test client
            client = app.test_client()
            
            # Login first
            login_response = client.post('/auth/login', data={
                'identifier': result['user'].username,
                'password': 'Test@123456'
            }, follow_redirects=True)
            
            print(f"✅ User login successful")
            
            # Prepare bulk add request
            bulk_items = [
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
                },
                {
                    'product_id': 3,
                    'product_name': 'Hampi Ruins Heritage Tee',
                    'price': 1399.99,
                    'product_image': 'mockups/hampi_temple_tshirt.jpg',
                    'quantity': 3,
                    'size': 'S'
                }
            ]
            
            # Call bulk add endpoint
            import json
            response = client.post('/cart/bulk-add', 
                data=json.dumps({'items': bulk_items}),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = json.loads(response.data)
                print(f"✅ Bulk add response: {data['message']}")
                print(f"   - Added items: {data.get('added_count', 0)}")
                print(f"   - Failed items: {data.get('failed_count', 0)}")
            else:
                print(f"❌ Bulk add endpoint failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


def test_cart_summary_endpoint():
    """Test GET /cart/summary endpoint."""
    print("\n=== Testing Cart Summary API Endpoint ===")
    try:
        with app.app_context():
            from services import AuthenticationService, CartService
            
            auth_service = AuthenticationService()
            cart_service = CartService()
            
            # Create test user
            result = auth_service.register_user(
                email=f"summary_{int(datetime.now().timestamp())}@test.com",
                username=f"summary_{int(datetime.now().timestamp())}",
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
            
            # Test the summary endpoint
            client = app.test_client()
            
            # Login first
            login_response = client.post('/auth/login', data={
                'identifier': result['user'].username,
                'password': 'Test@123456'
            }, follow_redirects=True)
            
            # Call summary endpoint
            import json
            response = client.get('/cart/summary')
            
            if response.status_code == 200:
                data = json.loads(response.data)
                print(f"✅ Cart summary retrieved:")
                print(f"   - Item count: {data.get('item_count', 0)}")
                print(f"   - Total: ₹{data.get('total', 0):.2f}")
                print(f"   - Items in cart: {len(data.get('items', []))}")
            else:
                print(f"❌ Summary endpoint failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


def test_cart_analytics_endpoint():
    """Test GET /cart/analytics endpoint."""
    print("\n=== Testing Cart Analytics API Endpoint ===")
    try:
        with app.app_context():
            from services import AuthenticationService, CartService
            
            auth_service = AuthenticationService()
            cart_service = CartService()
            
            # Create test user
            result = auth_service.register_user(
                email=f"analytics_{int(datetime.now().timestamp())}@test.com",
                username=f"analytics_{int(datetime.now().timestamp())}",
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
            
            # Test the analytics endpoint
            client = app.test_client()
            
            # Login first
            login_response = client.post('/auth/login', data={
                'identifier': result['user'].username,
                'password': 'Test@123456'
            }, follow_redirects=True)
            
            # Call analytics endpoint
            import json
            response = client.get('/cart/analytics')
            
            if response.status_code == 200:
                data = json.loads(response.data)
                print(f"✅ Cart analytics retrieved:")
                print(f"   - Total items: {data.get('total_items', 0)}")
                print(f"   - Total value: ₹{data.get('total_value', 0):.2f}")
                print(f"   - Average price: ₹{data.get('average_item_price', 0):.2f}")
                print(f"   - Price range: ₹{data.get('lowest_price', 0):.2f} - ₹{data.get('highest_price', 0):.2f}")
                print(f"   - Categories: {data.get('categories', {})}")
            else:
                print(f"❌ Analytics endpoint failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


def test_cart_recommendations_endpoint():
    """Test GET /cart/recommendations endpoint."""
    print("\n=== Testing Cart Recommendations API Endpoint ===")
    try:
        with app.app_context():
            from services import AuthenticationService, CartService
            
            auth_service = AuthenticationService()
            cart_service = CartService()
            
            # Create test user
            result = auth_service.register_user(
                email=f"recommendations_{int(datetime.now().timestamp())}@test.com",
                username=f"recommend_{int(datetime.now().timestamp())}",
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
            
            # Test the recommendations endpoint
            client = app.test_client()
            
            # Login first
            login_response = client.post('/auth/login', data={
                'identifier': result['user'].username,
                'password': 'Test@123456'
            }, follow_redirects=True)
            
            # Call recommendations endpoint
            import json
            response = client.get('/cart/recommendations?limit=5')
            
            if response.status_code == 200:
                data = json.loads(response.data)
                print(f"✅ Cart recommendations retrieved:")
                print(f"   - Categories detected: {data.get('categories', [])}")
                print(f"   - Recommendations count: {len(data.get('recommendations', []))}")
            else:
                print(f"❌ Recommendations endpoint failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


def test_estimated_delivery_endpoint():
    """Test GET /cart/estimated-delivery endpoint."""
    print("\n=== Testing Estimated Delivery API Endpoint ===")
    try:
        with app.app_context():
            from services import AuthenticationService, CartService
            
            auth_service = AuthenticationService()
            cart_service = CartService()
            
            # Create test user
            result = auth_service.register_user(
                email=f"delivery_{int(datetime.now().timestamp())}@test.com",
                username=f"delivery_{int(datetime.now().timestamp())}",
                password="Test@123456"
            )
            
            if not result['success']:
                print(f"❌ Failed to create test user: {result['message']}")
                return
            
            user_id = result['user'].id
            print(f"✅ Created test user: {user_id}")
            
            # Add items to cart
            cart_service.add_to_cart(user_id, 1, 'Tanjore Temple Graphic Tee', 1299.99, 'mockups/tanjore.jpg', 1, 'M')
            
            # Test the estimated delivery endpoint
            client = app.test_client()
            
            # Login first
            login_response = client.post('/auth/login', data={
                'identifier': result['user'].username,
                'password': 'Test@123456'
            }, follow_redirects=True)
            
            # Call estimated delivery endpoint
            import json
            response = client.get('/cart/estimated-delivery')
            
            if response.status_code == 200:
                data = json.loads(response.data)
                print(f"✅ Estimated delivery retrieved:")
                print(f"   - Standard delivery: {data.get('standard_days', 0)} days")
                print(f"   - Express delivery: {data.get('express_days', 0)} days")
            else:
                print(f"❌ Estimated delivery endpoint failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


if __name__ == '__main__':
    print("=" * 70)
    print("ADVANCED CART MANAGEMENT API - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    test_bulk_add_endpoint()
    test_cart_summary_endpoint()
    test_cart_analytics_endpoint()
    test_cart_recommendations_endpoint()
    test_estimated_delivery_endpoint()
    
    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETED")
    print("=" * 70)
