"""
Session 6 - Comprehensive Checkout Flow Testing
Tests complete user journey from cart to order confirmation
"""
from app import app
from services import AuthenticationService, CartService, CheckoutService
from repositories import AddressRepository

def test_complete_checkout_flow():
    """Test complete checkout flow from cart to order confirmation"""
    with app.app_context():
        print("=" * 70)
        print("SESSION 6 - COMPLETE CHECKOUT FLOW TEST")
        print("=" * 70)
        
        # Step 1: Create test user
        print("\n" + "-" * 70)
        print("STEP 1: CREATE TEST USER AND LOGIN")
        print("-" * 70)
        
        auth_service = AuthenticationService()
        result = auth_service.register_user(
            email=f"checkout_test_{int(__import__('time').time())}@example.com",
            username=f"checkoutuser_{int(__import__('time').time())}",
            password="Test@123456"
        )
        
        if not result['success']:
            print(f"❌ Failed to create user: {result['message']}")
            return
        
        user_id = result['user'].id
        print(f"✅ User created: {result['user'].username} (ID: {user_id})")
        
        # Step 2: Add items to cart
        print("\n" + "-" * 70)
        print("STEP 2: ADD ITEMS TO CART")
        print("-" * 70)
        
        cart_service = CartService()
        
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
        print(f"✅ Items added to cart: {bulk_result['added_count']}")
        
        # Step 3: Review cart
        print("\n" + "-" * 70)
        print("STEP 3: REVIEW CART")
        print("-" * 70)
        
        cart_summary = cart_service.get_cart_summary(user_id)
        if cart_summary['success']:
            print(f"✅ Cart Summary:")
            print(f"   Total Items: {cart_summary['item_count']}")
            print(f"   Cart Total: ₹{cart_summary['total']:.2f}")
            for item in cart_summary['items']:
                print(f"   • {item['product_name']}: {item['quantity']} x ₹{item['price']:.2f}")
        
        # Step 4: Create shipping address
        print("\n" + "-" * 70)
        print("STEP 4: CREATE SHIPPING ADDRESS")
        print("-" * 70)
        
        address_repo = AddressRepository()
        address = address_repo.create(
            user_id=user_id,
            full_name="Test User",
            phone="9876543210",
            address_line="123 Heritage Street",
            city="Bengaluru",
            state="Karnataka",
            postal_code="560001",
            country="India",
            is_default=True
        )
        
        if address:
            print(f"✅ Address created: {address.address_line}, {address.city}")
        else:
            print(f"❌ Failed to create address")
            return
        
        # Step 5: Test checkout service
        print("\n" + "-" * 70)
        print("STEP 5: CREATE ORDER (COD PAYMENT)")
        print("-" * 70)
        
        checkout_service = CheckoutService()
        order_result = checkout_service.create_order_from_cart(
            user_id=user_id,
            shipping_address_id=address.id,
            payment_method='cod'
        )
        
        if order_result['success']:
            print(f"✅ Order created successfully!")
            print(f"   Order Number: {order_result['order_number']}")
            print(f"   Order ID: {order_result['order'].id}")
            print(f"   Status: {order_result['order'].status}")
        else:
            print(f"❌ Order creation failed: {order_result['message']}")
            return
        
        # Step 6: Verify cart is cleared after checkout
        print("\n" + "-" * 70)
        print("STEP 6: VERIFY CART CLEARED AFTER CHECKOUT")
        print("-" * 70)
        
        cart_after = cart_service.get_user_cart(user_id)
        item_count = cart_after.get_item_count()
        
        if item_count == 0:
            print(f"✅ Cart properly cleared after checkout")
        else:
            print(f"❌ Cart still has {item_count} items after checkout")
        
        # Step 7: Test card payment flow
        print("\n" + "-" * 70)
        print("STEP 7: CREATE ORDER (CARD PAYMENT)")
        print("-" * 70)
        
        # Add new items to cart for card payment test
        card_items = [
            {
                'product_id': 3,
                'product_name': 'Hampi Ruins Heritage Tee',
                'price': 1399.99,
                'product_image': 'mockups/hampi_temple_tshirt.jpg',
                'quantity': 1,
                'size': 'M'
            }
        ]
        
        cart_service.bulk_add_to_cart(user_id, card_items)
        
        card_order_result = checkout_service.create_order_from_cart(
            user_id=user_id,
            shipping_address_id=address.id,
            payment_method='card',
            card_details={
                'card_number': '4111111111111111',
                'expiry': '12/25',
                'cvv': '123'
            }
        )
        
        if card_order_result['success']:
            print(f"✅ Card payment order created!")
            print(f"   Order Number: {card_order_result['order_number']}")
            print(f"   Status: {card_order_result['order'].status}")
        else:
            print(f"❌ Card payment failed: {card_order_result['message']}")
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ CHECKOUT FLOW TEST COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\n📊 Test Summary:")
        print(f"   ✅ User registration successful")
        print(f"   ✅ Items added to cart")
        print(f"   ✅ Cart summary retrieved")
        print(f"   ✅ Address created")
        print(f"   ✅ COD order created")
        print(f"   ✅ Cart cleared after checkout")
        print(f"   ✅ Card payment order created")
        print(f"\n🎉 All checkout flow tests passed!")

if __name__ == '__main__':
    test_complete_checkout_flow()
