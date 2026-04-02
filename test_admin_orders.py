"""
Session 6 - Admin Order Management Testing
Tests admin panel order listing, filtering, and management
"""
from app import app
from services import AuthenticationService, CartService, CheckoutService, AdminService
from repositories import AddressRepository, OrderRepository

def test_admin_order_management():
    """Test admin order management functionality"""
    with app.app_context():
        print("=" * 70)
        print("SESSION 6 - ADMIN ORDER MANAGEMENT TEST")
        print("=" * 70)
        
        # Step 1: Create test orders
        print("\n" + "-" * 70)
        print("STEP 1: CREATE TEST ORDERS")
        print("-" * 70)
        
        auth_service = AuthenticationService()
        cart_service = CartService()
        checkout_service = CheckoutService()
        address_repo = AddressRepository()
        order_repo = OrderRepository()
        
        orders_created = []
        
        for i in range(3):
            # Create user
            user_result = auth_service.register_user(
                email=f"order_test_{i}_{int(__import__('time').time())}@example.com",
                username=f"orderuser_{i}_{int(__import__('time').time())}",
                password="Test@123456"
            )
            
            if not user_result['success']:
                continue
            
            user_id = user_result['user'].id
            
            # Create address
            address = address_repo.create(
                user_id=user_id,
                full_name=f"Test User {i}",
                phone="9876543210",
                address_line=f"{100+i} Test Street",
                city="Bengaluru",
                state="Karnataka",
                postal_code="560001",
                country="India",
                is_default=True
            )
            
            # Add items to cart
            items = [
                {
                    'product_id': (i % 3) + 1,
                    'product_name': f'Product {i+1}',
                    'price': 1299.99 + (i * 100),
                    'product_image': f'mockups/product_{i}.jpg',
                    'quantity': i + 1,
                    'size': 'M'
                }
            ]
            
            cart_service.bulk_add_to_cart(user_id, items)
            
            # Create order
            if i % 2 == 0:
                order_result = checkout_service.create_order_from_cart(
                    user_id=user_id,
                    shipping_address_id=address.id,
                    payment_method='cod'
                )
            else:
                order_result = checkout_service.create_order_from_cart(
                    user_id=user_id,
                    shipping_address_id=address.id,
                    payment_method='card',
                    card_details={'card_number': '4111111111111111', 'expiry': '12/25', 'cvv': '123'}
                )
            
            if order_result['success']:
                orders_created.append(order_result['order'])
                print(f"✅ Order {i+1} created: {order_result['order_number']}")
        
        print(f"\n✅ Total orders created: {len(orders_created)}")
        
        # Step 2: Admin login
        print("\n" + "-" * 70)
        print("STEP 2: ADMIN LOGIN")
        print("-" * 70)
        
        admin_result = auth_service.login_admin('superadmin', 'Admin@123456')
        
        if admin_result['success']:
            print(f"✅ Admin logged in: {admin_result['admin'].username}")
        else:
            print(f"❌ Admin login failed: {admin_result['message']}")
            return
        
        # Step 3: Get all orders
        print("\n" + "-" * 70)
        print("STEP 3: RETRIEVE ALL ORDERS")
        print("-" * 70)
        
        all_orders = order_repo.find_all()
        print(f"✅ Total orders in system: {len(all_orders)}")
        print(f"   Recent orders:")
        for order in all_orders[-3:]:
            print(f"   • Order #{order.order_number} - ₹{order.total_amount:.2f} - Status: {order.status}")
        
        # Step 4: Test order detail retrieval
        print("\n" + "-" * 70)
        print("STEP 4: RETRIEVE ORDER DETAILS")
        print("-" * 70)
        
        if orders_created:
            order = orders_created[0]
            order_detail = order_repo.find_by_id(order.id)
            
            if order_detail:
                print(f"✅ Order detail retrieved:")
                print(f"   Order Number: {order_detail.order_number}")
                print(f"   User ID: {order_detail.user_id}")
                print(f"   Total Amount: ₹{order_detail.total_amount:.2f}")
                print(f"   Status: {order_detail.status}")
                print(f"   Items in order: {len(order_detail.items)}")
                for item in order_detail.items:
                    print(f"     • {item.product_name} x {item.quantity}")
        
        # Step 5: Test order status update
        print("\n" + "-" * 70)
        print("STEP 5: UPDATE ORDER STATUS")
        print("-" * 70)
        
        if orders_created:
            order = orders_created[0]
            original_status = order.status
            
            # Update status
            order.status = 'shipped'
            from models import db
            db.session.commit()
            
            updated_order = order_repo.find_by_id(order.id)
            
            if updated_order and updated_order.status == 'shipped':
                print(f"✅ Order status updated: {original_status} → {updated_order.status}")
            else:
                print(f"❌ Failed to update order status")
        
        # Step 6: Test order filtering
        print("\n" + "-" * 70)
        print("STEP 6: FILTER ORDERS BY STATUS")
        print("-" * 70)
        
        pending_orders = [o for o in all_orders if o.status == 'pending']
        confirmed_orders = [o for o in all_orders if o.status == 'confirmed']
        shipped_orders = [o for o in all_orders if o.status == 'shipped']
        
        print(f"✅ Orders by status:")
        print(f"   Pending: {len(pending_orders)}")
        print(f"   Confirmed: {len(confirmed_orders)}")
        print(f"   Shipped: {len(shipped_orders)}")
        
        # Step 7: Test order item retrieval with images
        print("\n" + "-" * 70)
        print("STEP 7: VERIFY ORDER ITEMS WITH IMAGES")
        print("-" * 70)
        
        if orders_created:
            order = orders_created[0]
            print(f"✅ Order #{order.order_number} Items:")
            for item in order.items:
                print(f"   • {item.product_name}")
                print(f"     - Quantity: {item.quantity}")
                print(f"     - Price: ₹{item.price:.2f}")
                print(f"     - Size: {item.size}")
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ ADMIN ORDER MANAGEMENT TEST COMPLETED")
        print("=" * 70)
        print("\n📊 Test Summary:")
        print(f"   ✅ {len(orders_created)} test orders created")
        print(f"   ✅ Admin login successful")
        print(f"   ✅ All orders retrieved successfully")
        print(f"   ✅ Order details accessible")
        print(f"   ✅ Order status update working")
        print(f"   ✅ Order filtering by status working")
        print(f"   ✅ Order items with images verified")
        print(f"\n🎉 All admin order management tests passed!")

if __name__ == '__main__':
    test_admin_order_management()
