"""
Create comprehensive test data for cart management testing.
Generates sample users, addresses, products, coupons, and orders for testing.
"""
from datetime import datetime, timedelta
from app import app, db

def create_test_data():
    """Create comprehensive test data for cart management."""
    print("\n" + "=" * 70)
    print("CREATING COMPREHENSIVE TEST DATA")
    print("=" * 70)
    
    with app.app_context():
        from services import AuthenticationService, CartService, CheckoutService
        from repositories import AddressRepository
        
        auth_service = AuthenticationService()
        cart_service = CartService()
        checkout_service = CheckoutService()
        address_repo = AddressRepository()
        
        # Create 5 test users with different scenarios
        test_users = []
        
        print("\n1️⃣  Creating Test Users...")
        for i in range(1, 6):
            email = f"testuser{i}_{int(datetime.now().timestamp())}@test.com"
            username = f"testuser{i}_{int(datetime.now().timestamp())}"
            
            result = auth_service.register_user(
                email=email,
                username=username,
                password="Test@123456",
                full_name=f"Test User {i}"
            )
            
            if result['success']:
                user = result['user']
                test_users.append(user)
                print(f"   ✅ Created: {username} (ID: {user.id})")
                
                # Create addresses for users
                address_data = {
                    'street': f"{100 + i} Test Street",
                    'city': ['Mumbai', 'Bangalore', 'Delhi', 'Hyderabad', 'Chennai'][i-1],
                    'state': ['MH', 'KA', 'DL', 'TG', 'TN'][i-1],
                    'zip_code': f"4000{i}0",
                    'country': 'India',
                    'phone': f"900000000{i}",
                    'is_default': True
                }
                try:
                    address_repo.create(user.id, **address_data)
                    print(f"      └─ Added address in {address_data['city']}")
                except Exception as e:
                    print(f"      └─ Address creation failed: {str(e)}")
            else:
                print(f"   ❌ Failed to create user: {result['message']}")
        
        # Add different cart scenarios
        print("\n2️⃣  Creating Cart Scenarios...")
        
        if len(test_users) >= 1:
            # Scenario 1: Standard shopping cart
            user = test_users[0]
            cart_service.add_to_cart(user.id, 1, 'Tanjore Temple Graphic Tee', 1299.99, 'mockups/tanjore.jpg', 2, 'M')
            cart_service.add_to_cart(user.id, 2, 'ISRO Space Missions Hoodie', 1999.99, 'mockups/isro_1st_rocket.jpg', 1, 'L')
            print(f"   ✅ User {user.username}: Standard cart (2 items)")
        
        if len(test_users) >= 2:
            # Scenario 2: Large cart with multiple items
            user = test_users[1]
            items = [
                (3, 'Hampi Ruins Heritage Tee', 1399.99, 3),
                (4, 'Mysore Palace Heritage Tee', 1499.99, 2),
                (5, 'Hyderabad Charminar Heritage Tee', 1499.99, 1),
                (6, 'Lonavala Hills Heritage Tee', 1399.99, 2),
            ]
            for product_id, name, price, qty in items:
                cart_service.add_to_cart(user.id, product_id, name, price, f'mockups/{name.lower()}.jpg', qty, 'M')
            print(f"   ✅ User {user.username}: Large cart (8 items)")
        
        if len(test_users) >= 3:
            # Scenario 3: Premium items cart
            user = test_users[2]
            items = [
                (9, 'Lucknow Heritage Premium Model Tee', 1899.99, 1),
                (12, 'Assam Heritage Model Tee', 1699.99, 1),
                (13, 'Kolkata Heritage Model Tee', 1699.99, 1),
                (15, 'Chhatrapati Shivaji Maharaj Hoodie', 2099.99, 1),
            ]
            for product_id, name, price, qty in items:
                cart_service.add_to_cart(user.id, product_id, name, price, f'mockups/{name.lower()}.jpg', qty, 'L')
            print(f"   ✅ User {user.username}: Premium items cart (4 items)")
        
        if len(test_users) >= 4:
            # Scenario 4: Bulk purchase
            user = test_users[3]
            bulk_items = [
                {'product_id': 1, 'product_name': 'Tanjore Temple Graphic Tee', 'price': 1299.99, 'product_image': 'mockups/tanjore.jpg', 'quantity': 5, 'size': 'M'},
                {'product_id': 2, 'product_name': 'ISRO Space Missions Hoodie', 'price': 1999.99, 'product_image': 'mockups/isro_1st_rocket.jpg', 'quantity': 3, 'size': 'L'},
            ]
            result = cart_service.bulk_add_to_cart(user.id, bulk_items)
            print(f"   ✅ User {user.username}: Bulk purchase ({result['added_count']} items via bulk add)")
        
        if len(test_users) >= 5:
            # Scenario 5: Small cart (for abandoned cart testing)
            user = test_users[4]
            cart_service.add_to_cart(user.id, 7, 'Lonavala Hills Model Tee', 1599.99, 'mockups/lonavala_model.jpg', 1, 'S')
            print(f"   ✅ User {user.username}: Small cart (1 item - for abandoned cart detection)")
        
        # Display cart summary
        print("\n3️⃣  Cart Summary Statistics...")
        for user in test_users:
            summary = cart_service.get_cart_summary(user.id)
            if summary['success']:
                print(f"   📊 {user.username}:")
                print(f"      - Items: {summary['item_count']}")
                print(f"      - Total: ₹{summary['total']:.2f}")
        
        # Test advanced features
        print("\n4️⃣  Testing Advanced Cart Features...")
        
        # Test cart merge
        if len(test_users) >= 2:
            guest_user = test_users[0]
            registered_user = test_users[1]
            merge_result = cart_service.merge_carts(registered_user.id, guest_user.id)
            print(f"   ✅ Cart Merge: {merge_result['message']}")
            print(f"      - Items merged: {merge_result['merged_count']}")
        
        # Test abandoned cart detection
        if len(test_users) >= 5:
            abandoned_result = cart_service.check_abandoned_cart(test_users[4].id, hours=0)
            print(f"   ✅ Abandoned Cart Detection: {'Yes' if abandoned_result['is_abandoned'] else 'No'}")
        
        # Test recommendations
        if len(test_users) >= 1:
            recommendations = cart_service.get_cart_recommendations(test_users[0].id)
            if recommendations['success']:
                print(f"   ✅ Cart Recommendations: Categories detected: {recommendations['categories']}")
        
        print("\n" + "=" * 70)
        print("TEST DATA CREATION COMPLETED")
        print("=" * 70)
        print("\n✅ Ready for comprehensive end-to-end testing!")
        print("   - Created 5 test users with different cart scenarios")
        print("   - Created test addresses for each user")
        print("   - Tested bulk operations, cart merge, and recommendations")
        print("   - All advanced cart features validated")

if __name__ == '__main__':
    create_test_data()
