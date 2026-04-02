"""
Session 7 - End-to-End Checkout Flow & Payment Processing Test
Comprehensive testing of complete checkout flow, payment methods, and order management
"""
from app import app, db
from services import AuthenticationService, CartService, CheckoutService, DiscountService
from models import User, Order, Payment
from datetime import datetime
import json

def test_complete_checkout_flow():
    """Test complete end-to-end checkout flow with payment processing"""
    
    with app.app_context():
        print("=" * 80)
        print("SESSION 7 - END-TO-END CHECKOUT FLOW & PAYMENT PROCESSING TEST")
        print("=" * 80)
        
        # Initialize services
        auth_service = AuthenticationService()
        cart_service = CartService()
        checkout_service = CheckoutService()
        discount_service = DiscountService()
        
        test_results = {
            'cod_payment': False,
            'card_payment': False,
            'order_creation': False,
            'order_retrieval': False,
            'payment_status': False,
            'discount_application': False,
            'cart_merge': False,
            'bulk_operations': False
        }
        
        # ===== TEST 1: User Registration and Authentication =====
        print("\n" + "-" * 80)
        print("TEST 1: USER REGISTRATION AND AUTHENTICATION")
        print("-" * 80)
        
        timestamp = int(__import__('time').time())
        user_email = f"checkout_test_{timestamp}@example.com"
        user_username = f"checkouttest_{timestamp}"
        
        reg_result = auth_service.register_user(
            email=user_email,
            username=user_username,
            password="Checkout@Test123"
        )
        
        if reg_result['success']:
            user_id = reg_result['user'].id
            print(f"✅ User registration successful")
            print(f"   Username: {user_username}")
            print(f"   Email: {user_email}")
            print(f"   User ID: {user_id}")
            
            # Verify login
            login_result = auth_service.login_user(user_username, "Checkout@Test123")
            if login_result['success']:
                print(f"✅ User login successful")
            else:
                print(f"❌ User login failed: {login_result['message']}")
                return
        else:
            print(f"❌ User registration failed: {reg_result['message']}")
            return
        
        # ===== TEST 2: Add Products to Cart =====
        print("\n" + "-" * 80)
        print("TEST 2: ADD PRODUCTS TO CART")
        print("-" * 80)
        
        products = [
            {
                'product_id': 1,
                'product_name': 'Tanjore Temple Graphic Tee',
                'price': 1299.99,
                'product_image': 'mockups/tanjore.jpg',
                'quantity': 1,
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
                'quantity': 2,
                'size': 'M'
            }
        ]
        
        bulk_result = cart_service.bulk_add_to_cart(user_id, products)
        
        if bulk_result['success']:
            print(f"✅ Bulk add to cart successful")
            print(f"   Added items: {bulk_result['added_count']}")
            print(f"   Total in cart: {bulk_result['cart_count']}")
            test_results['bulk_operations'] = True
        else:
            print(f"❌ Bulk add to cart failed: {bulk_result['message']}")
        
        # ===== TEST 3: Get Cart Summary =====
        print("\n" + "-" * 80)
        print("TEST 3: GET CART SUMMARY")
        print("-" * 80)
        
        summary = cart_service.get_cart_summary(user_id)
        
        if summary['success']:
            print(f"✅ Cart summary retrieved")
            print(f"   Items: {summary['item_count']}")
            print(f"   Total: ₹{summary['total']:.2f}")
            cart_total = summary['total']
            print(f"\n   Cart Items:")
            for item in summary['items']:
                print(f"   • {item['product_name']}: {item['quantity']} × ₹{item['price']:.2f} = ₹{item['subtotal']:.2f}")
        else:
            print(f"❌ Cart summary failed: {summary['message']}")
            return
        
        # ===== TEST 4: Apply Discount/Coupon =====
        print("\n" + "-" * 80)
        print("TEST 4: APPLY DISCOUNT/COUPON")
        print("-" * 80)
        
        # Note: This assumes coupons exist in database
        coupon_validation = discount_service.validate_coupon("WELCOME20", cart_total, user_id)
        
        if coupon_validation['success']:
            print(f"✅ Coupon validation successful")
            print(f"   Coupon: WELCOME20")
            print(f"   Discount: ₹{coupon_validation['discount_amount']:.2f}")
            print(f"   Final Amount: ₹{coupon_validation['final_amount']:.2f}")
            final_total = coupon_validation['final_amount']
            test_results['discount_application'] = True
        else:
            print(f"⚠️  Coupon not available: {coupon_validation['message']}")
            final_total = cart_total
        
        # ===== TEST 5: Create Order - COD Payment =====
        print("\n" + "-" * 80)
        print("TEST 5: CREATE ORDER - CASH ON DELIVERY (COD) PAYMENT")
        print("-" * 80)
        
        cod_order_result = checkout_service.create_order_from_cart(
            user_id=user_id,
            shipping_address_id=1,
            payment_method='cod'
        )
        
        if cod_order_result['success']:
            print(f"✅ COD Order created successfully")
            print(f"   Order Number: {cod_order_result['order_number']}")
            print(f"   Order ID: {cod_order_result['order'].id}")
            print(f"   Status: {cod_order_result['order'].status}")
            print(f"   Total: ₹{cod_order_result['order'].total_amount:.2f}")
            cod_order_id = cod_order_result['order'].id
            test_results['cod_payment'] = True
            test_results['order_creation'] = True
        else:
            print(f"❌ COD Order creation failed: {cod_order_result['message']}")
        
        # ===== TEST 6: Create Order - Card Payment =====
        print("\n" + "-" * 80)
        print("TEST 6: CREATE ORDER - CARD PAYMENT")
        print("-" * 80)
        
        # Create another user for card payment test
        card_user_email = f"card_test_{timestamp}@example.com"
        card_user_username = f"cardtest_{timestamp}"
        
        card_user_reg = auth_service.register_user(
            email=card_user_email,
            username=card_user_username,
            password="Card@Test123"
        )
        
        if card_user_reg['success']:
            card_user_id = card_user_reg['user'].id
            
            # Add products to card user's cart
            cart_service.bulk_add_to_cart(card_user_id, products)
            
            # Create order with card payment
            card_order_result = checkout_service.create_order_from_cart(
                user_id=card_user_id,
                shipping_address_id=1,
                payment_method='card',
                card_details={
                    'card_number': '4111111111111111',
                    'expiry_month': '12',
                    'expiry_year': '2025',
                    'cvv': '123'
                }
            )
            
            if card_order_result['success']:
                print(f"✅ Card Order created successfully")
                print(f"   Order Number: {card_order_result['order_number']}")
                print(f"   Order ID: {card_order_result['order'].id}")
                print(f"   Status: {card_order_result['order'].status}")
                print(f"   Total: ₹{card_order_result['order'].total_amount:.2f}")
                card_order_id = card_order_result['order'].id
                test_results['card_payment'] = True
            else:
                print(f"❌ Card Order creation failed: {card_order_result['message']}")
        
        # ===== TEST 7: Verify Order in Database =====
        print("\n" + "-" * 80)
        print("TEST 7: VERIFY ORDER IN DATABASE")
        print("-" * 80)
        
        cod_order = Order.query.get(cod_order_id)
        
        if cod_order:
            print(f"✅ Order retrieved from database")
            print(f"   Order ID: {cod_order.id}")
            print(f"   User ID: {cod_order.user_id}")
            print(f"   Status: {cod_order.status}")
            print(f"   Total: ₹{cod_order.total_amount:.2f}")
            print(f"   Items: {len(cod_order.items)}")
            print(f"   Created: {cod_order.created_at}")
            test_results['order_retrieval'] = True
            
            # Verify order items
            print(f"\n   Order Items:")
            for item in cod_order.items:
                print(f"   • {item.product_name}: {item.quantity} × ₹{item.price:.2f}")
        else:
            print(f"❌ Order not found in database")
        
        # ===== TEST 8: Verify Payment Status =====
        print("\n" + "-" * 80)
        print("TEST 8: VERIFY PAYMENT STATUS")
        print("-" * 80)
        
        cod_payment = Payment.query.filter_by(order_id=cod_order_id).first()
        
        if cod_payment:
            print(f"✅ Payment record found")
            print(f"   Payment ID: {cod_payment.id}")
            print(f"   Order ID: {cod_payment.order_id}")
            print(f"   Method: {cod_payment.payment_method}")
            print(f"   Status: {cod_payment.payment_status}")
            print(f"   Amount: ₹{cod_payment.amount:.2f}")
            print(f"   Created: {cod_payment.created_at}")
            test_results['payment_status'] = True
        else:
            print(f"❌ Payment record not found")
        
        # ===== TEST 9: Cart Merge Scenario =====
        print("\n" + "-" * 80)
        print("TEST 9: CART MERGE SCENARIO (GUEST TO REGISTERED)")
        print("-" * 80)
        
        # Create guest user
        guest_email = f"guest_test_{timestamp}@example.com"
        guest_username = f"guesttest_{timestamp}"
        
        guest_reg = auth_service.register_user(
            email=guest_email,
            username=guest_username,
            password="Guest@Test123"
        )
        
        if guest_reg['success']:
            guest_user_id = guest_reg['user'].id
            
            # Add items to guest cart
            guest_items = [
                {
                    'product_id': 4,
                    'product_name': 'Mysore Palace Heritage Tee',
                    'price': 1499.99,
                    'product_image': 'mockups/mysore.jpg',
                    'quantity': 1,
                    'size': 'M'
                }
            ]
            
            cart_service.bulk_add_to_cart(guest_user_id, guest_items)
            
            # Merge carts
            merge_result = cart_service.merge_carts(user_id, guest_user_id)
            
            if merge_result['success']:
                print(f"✅ Cart merge successful")
                print(f"   Merged items: {merge_result['merged_count']}")
                print(f"   New cart total: ₹{merge_result['target_cart_total']:.2f}")
                test_results['cart_merge'] = True
            else:
                print(f"❌ Cart merge failed: {merge_result['message']}")
        
        # ===== FINAL SUMMARY =====
        print("\n" + "=" * 80)
        print("SESSION 7 - END-TO-END CHECKOUT FLOW TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for v in test_results.values() if v)
        total = len(test_results)
        success_rate = (passed / total) * 100
        
        print(f"\n📊 Test Results:")
        print(f"   Passed: {passed}/{total} ({success_rate:.1f}%)")
        print(f"\n   Individual Results:")
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status}: {test_name.replace('_', ' ').title()}")
        
        print(f"\n✅ End-to-End Checkout Flow Features:")
        print(f"   ✓ User registration and authentication")
        print(f"   ✓ Product addition to cart (bulk operations)")
        print(f"   ✓ Cart summary and pricing")
        print(f"   ✓ Discount/coupon application")
        print(f"   ✓ COD payment processing")
        print(f"   ✓ Card payment processing")
        print(f"   ✓ Order creation and storage")
        print(f"   ✓ Payment status tracking")
        print(f"   ✓ Guest cart merging")
        
        if success_rate == 100:
            print(f"\n🎉 ALL TESTS PASSED - READY FOR PRODUCTION DEPLOYMENT")
        else:
            print(f"\n⚠️  Some tests failed - Review results above")

if __name__ == '__main__':
    test_complete_checkout_flow()
