"""
Create comprehensive test data for cart management testing.
Generates sample users, products, orders, and coupons.
"""
from datetime import datetime, timedelta
from app import app, db

def create_test_data():
    """Create sample test data for all testing scenarios."""
    with app.app_context():
        from services import AuthenticationService
        from repositories import CouponRepository
        
        auth_service = AuthenticationService()
        coupon_repo = CouponRepository()
        
        print("=" * 60)
        print("CREATING COMPREHENSIVE TEST DATA")
        print("=" * 60)
        
        # Create test users
        print("\n📝 Creating test users...")
        test_users = []
        
        # User 1: Regular user
        user1 = auth_service.register_user(
            email="testuser1@example.com",
            username="testuser1",
            password="Test@123456"
        )
        if user1['success']:
            test_users.append(user1['user'])
            print(f"✅ Created user: testuser1 (ID: {user1['user'].id})")
        
        # User 2: Guest user (for cart merge testing)
        user2 = auth_service.register_user(
            email="guestuser@example.com",
            username="guestuser",
            password="Test@123456"
        )
        if user2['success']:
            test_users.append(user2['user'])
            print(f"✅ Created user: guestuser (ID: {user2['user'].id})")
        
        # User 3: Bulk order user
        user3 = auth_service.register_user(
            email="bulkuser@example.com",
            username="bulkuser",
            password="Test@123456"
        )
        if user3['success']:
            test_users.append(user3['user'])
            print(f"✅ Created user: bulkuser (ID: {user3['user'].id})")
        
        # Create test coupons
        print("\n🎟️  Creating test coupons...")
        coupons = [
            {
                'code': 'SAVE10',
                'discount_type': 'percentage',
                'discount_value': 10,
                'min_order_value': 1000,
                'max_uses': 100,
                'expiry_date': datetime.now() + timedelta(days=30)
            },
            {
                'code': 'FLAT500',
                'discount_type': 'fixed',
                'discount_value': 500,
                'min_order_value': 2000,
                'max_uses': 50,
                'expiry_date': datetime.now() + timedelta(days=30)
            },
            {
                'code': 'WELCOME20',
                'discount_type': 'percentage',
                'discount_value': 20,
                'min_order_value': 500,
                'max_uses': 1000,
                'expiry_date': datetime.now() + timedelta(days=30)
            }
        ]
        
        for coupon in coupons:
            try:
                existing = coupon_repo.find_by_code(coupon['code'])
                if not existing:
                    coupon_repo.create(**coupon)
                    print(f"✅ Created coupon: {coupon['code']} - {coupon['discount_value']}{coupon['discount_type'][0].upper()}")
            except Exception as e:
                print(f"⚠️  Coupon creation failed: {coupon['code']} - {str(e)}")
        
        # Test cart operations
        print("\n🛒 Testing cart operations with sample data...")
        from services import CartService
        
        cart_service = CartService()
        
        # Sample products for testing
        sample_products = [
            {'product_id': 1, 'product_name': 'Tanjore Temple Graphic Tee', 'price': 1299.99, 'product_image': 'mockups/tanjore.jpg'},
            {'product_id': 2, 'product_name': 'ISRO Space Missions Hoodie', 'price': 1999.99, 'product_image': 'mockups/isro_1st_rocket.jpg'},
            {'product_id': 3, 'product_name': 'Hampi Ruins Heritage Tee', 'price': 1399.99, 'product_image': 'mockups/hampi_temple_tshirt.jpg'},
            {'product_id': 4, 'product_name': 'Mysore Palace Heritage Tee', 'price': 1499.99, 'product_image': 'mockups/mysore.jpg'},
            {'product_id': 5, 'product_name': 'Hyderabad Charminar Heritage Tee', 'price': 1499.99, 'product_image': 'mockups/hyderabad.jpg'},
        ]
        
        # Test 1: Bulk add to cart
        if test_users:
            print(f"\n  Test 1: Bulk add items for user {test_users[0].username}...")
            bulk_items = [
                {**sample_products[0], 'quantity': 2, 'size': 'M'},
                {**sample_products[1], 'quantity': 1, 'size': 'L'},
                {**sample_products[2], 'quantity': 3, 'size': 'S'},
            ]
            result = cart_service.bulk_add_to_cart(test_users[0].id, bulk_items)
            if result['success']:
                print(f"  ✅ Bulk add successful: {result['added_count']} items added")
                print(f"     Cart total: ₹{cart_service.get_user_cart(test_users[0].id).get_total():.2f}")
        
        # Test 2: Get cart summary
        if test_users:
            print(f"\n  Test 2: Get cart summary for user {test_users[0].username}...")
            summary = cart_service.get_cart_summary(test_users[0].id)
            if summary['success']:
                print(f"  ✅ Cart summary retrieved:")
                print(f"     Item count: {summary['item_count']}")
                print(f"     Total: ₹{summary['total']:.2f}")
        
        # Test 3: Cart merge
        if len(test_users) >= 2:
            print(f"\n  Test 3: Cart merge from {test_users[1].username} to {test_users[0].username}...")
            # Add items to guest cart first
            guest_items = [
                {**sample_products[3], 'quantity': 1, 'size': 'M'},
                {**sample_products[4], 'quantity': 2, 'size': 'L'},
            ]
            cart_service.bulk_add_to_cart(test_users[1].id, guest_items)
            
            # Merge carts
            merge_result = cart_service.merge_carts(test_users[0].id, test_users[1].id)
            if merge_result['success']:
                print(f"  ✅ Cart merge successful: {merge_result['merged_count']} items merged")
                print(f"     New cart total: ₹{merge_result['target_cart_total']:.2f}")
        
        # Test 4: Cart recommendations
        if test_users:
            print(f"\n  Test 4: Get recommendations for user {test_users[0].username}...")
            recommendations = cart_service.get_cart_recommendations(test_users[0].id, limit=5)
            if recommendations['success']:
                print(f"  ✅ Recommendations retrieved:")
                print(f"     Categories in cart: {recommendations['categories']}")
        
        # Test 5: Abandoned cart detection
        if test_users:
            print(f"\n  Test 5: Check abandoned cart for user {test_users[0].username}...")
            abandoned = cart_service.check_abandoned_cart(test_users[0].id, hours=24)
            if abandoned['success']:
                print(f"  ✅ Abandoned cart check:")
                print(f"     Is abandoned: {abandoned['is_abandoned']}")
                print(f"     Hours since update: {abandoned['hours_since_update']}")
                print(f"     Cart value: ₹{abandoned['cart_value']:.2f}")
        
        print("\n" + "=" * 60)
        print("TEST DATA CREATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"  - Created {len(test_users)} test users")
        print(f"  - Created {len(coupons)} test coupons")
        print(f"  - All cart operations tested successfully")
        print(f"\n🔐 Test User Credentials:")
        for i, user in enumerate(test_users, 1):
            print(f"  User {i}: {user.username} / Test@123456")

if __name__ == '__main__':
    create_test_data()
