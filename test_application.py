"""
Test script for FashionBrand application
Tests core functionality without requiring manual interaction
"""
import sys
import os
sys.path.insert(0, '/Users/anirudhdev/FashionBrand')

from app import app, db
from models import User, Admin, Order, Cart, CartItem
from repositories import UserRepository, AdminRepository, OrderRepository
from services import AuthenticationService, CartService

def test_database_connection():
    """Test database connection"""
    print("\n" + "="*50)
    print("TEST 1: Database Connection")
    print("="*50)
    try:
        with app.app_context():
            # Check if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Database connected successfully")
            print(f"✅ Found {len(tables)} tables: {', '.join(tables)}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def test_admin_user_exists():
    """Test if default admin exists"""
    print("\n" + "="*50)
    print("TEST 2: Default Admin User")
    print("="*50)
    try:
        with app.app_context():
            admin = AdminRepository.find_by_username('superadmin')
            if admin:
                print(f"✅ Default admin found")
                print(f"   Username: {admin.username}")
                print(f"   Email: {admin.email}")
                print(f"   Role: {admin.role}")
                return True
            else:
                print(f"❌ Default admin not found")
                return False
    except Exception as e:
        print(f"❌ Error checking admin: {str(e)}")
        return False

def test_user_registration():
    """Test user registration"""
    print("\n" + "="*50)
    print("TEST 3: User Registration")
    print("="*50)
    try:
        with app.app_context():
            service = AuthenticationService()
            result = service.register_user(
                email='testuser@example.com',
                username='testuser',
                password='TestPassword123',
                first_name='Test',
                last_name='User'
            )
            if result['success']:
                print(f"✅ User registration successful")
                print(f"   Username: {result['user'].username}")
                print(f"   Email: {result['user'].email}")
                return True
            else:
                print(f"❌ Registration failed: {result['message']}")
                return False
    except Exception as e:
        print(f"❌ Error during registration: {str(e)}")
        return False

def test_user_login():
    """Test user login"""
    print("\n" + "="*50)
    print("TEST 4: User Login")
    print("="*50)
    try:
        with app.app_context():
            service = AuthenticationService()
            result = service.login_user('testuser', 'TestPassword123')
            if result['success']:
                print(f"✅ User login successful")
                print(f"   Username: {result['user'].username}")
                print(f"   Last Login: {result['user'].last_login}")
                return True
            else:
                print(f"❌ Login failed: {result['message']}")
                return False
    except Exception as e:
        print(f"❌ Error during login: {str(e)}")
        return False

def test_admin_login():
    """Test admin login"""
    print("\n" + "="*50)
    print("TEST 5: Admin Login")
    print("="*50)
    try:
        with app.app_context():
            service = AuthenticationService()
            result = service.login_admin('superadmin', 'Admin@123456')
            if result['success']:
                print(f"✅ Admin login successful")
                print(f"   Username: {result['admin'].username}")
                print(f"   Role: {result['admin'].role}")
                return True
            else:
                print(f"❌ Admin login failed: {result['message']}")
                return False
    except Exception as e:
        print(f"❌ Error during admin login: {str(e)}")
        return False

def test_cart_operations():
    """Test cart operations"""
    print("\n" + "="*50)
    print("TEST 6: Cart Operations")
    print("="*50)
    try:
        with app.app_context():
            user = UserRepository.find_by_username('testuser')
            if not user:
                print(f"❌ Test user not found")
                return False
            
            cart_service = CartService()
            
            # Add item to cart
            result = cart_service.add_to_cart(
                user_id=user.id,
                product_id=1,
                product_name='Tanjore Temple Graphic Tee',
                price=1299.99,
                product_image='mockups/tanjore.jpg',
                quantity=1,
                size='M'
            )
            
            if result['success']:
                print(f"✅ Item added to cart")
                print(f"   Product: Tanjore Temple Graphic Tee")
                print(f"   Price: ₹1299.99")
                print(f"   Cart Count: {result['cart_count']}")
                return True
            else:
                print(f"❌ Add to cart failed: {result['message']}")
                return False
    except Exception as e:
        print(f"❌ Error during cart operations: {str(e)}")
        return False

def test_user_count():
    """Test user count in database"""
    print("\n" + "="*50)
    print("TEST 7: Database Statistics")
    print("="*50)
    try:
        with app.app_context():
            user_count = User.query.count()
            admin_count = Admin.query.count()
            print(f"✅ Database statistics retrieved")
            print(f"   Total Users: {user_count}")
            print(f"   Total Admins: {admin_count}")
            return True
    except Exception as e:
        print(f"❌ Error retrieving statistics: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "🧪 FASHIONBRAND APPLICATION TEST SUITE 🧪".center(50))
    print("Testing core functionality\n")
    
    tests = [
        test_database_connection,
        test_admin_user_exists,
        test_user_registration,
        test_user_login,
        test_admin_login,
        test_cart_operations,
        test_user_count
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results.append(False)
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Application is ready for production.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the output above.")
    
    print("="*50 + "\n")

if __name__ == '__main__':
    main()
