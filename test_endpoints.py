"""
Test API endpoints and routes
"""
import requests
import json
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5001"

def test_public_routes():
    """Test public routes"""
    print("\n" + "="*60)
    print("TEST: Public Routes")
    print("="*60)
    
    routes = [
        ('/', 'Home Page'),
        ('/shop', 'Shop Page'),
        ('/about', 'About Page'),
        ('/contact', 'Contact Page'),
        ('/indian-heritage', 'Indian Heritage Page'),
        ('/product/1', 'Product Detail Page'),
    ]
    
    for route, name in routes:
        try:
            response = requests.get(f"{BASE_URL}{route}")
            if response.status_code == 200:
                print(f"✅ {name}: {response.status_code}")
            else:
                print(f"❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")

def test_auth_routes():
    """Test authentication routes"""
    print("\n" + "="*60)
    print("TEST: Authentication Routes")
    print("="*60)
    
    routes = [
        ('/auth/login', 'User Login Page'),
        ('/auth/register', 'User Register Page'),
        ('/auth/admin/login', 'Admin Login Page'),
        ('/auth/admin/register', 'Admin Register Page'),
    ]
    
    for route, name in routes:
        try:
            response = requests.get(f"{BASE_URL}{route}")
            if response.status_code in [200, 302]:  # 302 is redirect for logged in users
                print(f"✅ {name}: {response.status_code}")
            else:
                print(f"❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")

def test_user_registration_flow():
    """Test user registration flow"""
    print("\n" + "="*60)
    print("TEST: User Registration Flow")
    print("="*60)
    
    # Get register page
    response = requests.get(f"{BASE_URL}/auth/register")
    if response.status_code == 200:
        print("✅ Register page loaded successfully")
    else:
        print(f"❌ Register page failed: {response.status_code}")
        return
    
    # Try to register new user
    registration_data = {
        'email': 'newuser@example.com',
        'username': 'newuser123',
        'password': 'Password123',
        'confirm_password': 'Password123',
        'first_name': 'New',
        'last_name': 'User',
        'phone': '+91-98765-43210'
    }
    
    session = requests.Session()
    response = session.post(f"{BASE_URL}/auth/register", data=registration_data)
    
    if response.status_code == 200 or response.url.endswith('/auth/login'):
        print("✅ Registration POST request succeeded")
    else:
        print(f"❌ Registration POST request failed: {response.status_code}")

def test_shop_page():
    """Test shop page and filtering"""
    print("\n" + "="*60)
    print("TEST: Shop Page and Filtering")
    print("="*60)
    
    filters = [
        ('all', 'All Products'),
        ('streetwear', 'Streetwear Category'),
        ('heritage', 'Heritage Category'),
        ('premium', 'Premium Category'),
    ]
    
    for category, name in filters:
        try:
            response = requests.get(f"{BASE_URL}/shop", params={'category': category})
            if response.status_code == 200:
                print(f"✅ {name}: {response.status_code}")
            else:
                print(f"❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")

def test_api_endpoints():
    """Test API endpoints"""
    print("\n" + "="*60)
    print("TEST: API Endpoints")
    print("="*60)
    
    # Test newsletter subscription
    subscribe_data = {
        'email': 'subscriber@example.com'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/subscribe",
            json=subscribe_data,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            print(f"✅ Newsletter Subscription API: {response.status_code}")
        else:
            print(f"⚠️ Newsletter Subscription API: {response.status_code}")
    except Exception as e:
        print(f"❌ Newsletter Subscription API: Error - {str(e)}")
    
    # Test contact form
    contact_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'message': 'Test message'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/contact",
            json=contact_data,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            print(f"✅ Contact Form API: {response.status_code}")
        else:
            print(f"⚠️ Contact Form API: {response.status_code}")
    except Exception as e:
        print(f"❌ Contact Form API: Error - {str(e)}")

def test_database_integrity():
    """Test database integrity"""
    print("\n" + "="*60)
    print("TEST: Database Integrity Check")
    print("="*60)
    
    import sys
    sys.path.insert(0, '/Users/anirudhdev/FashionBrand')
    from app import app, db
    from models import User, Admin, Order, Address, Cart
    
    with app.app_context():
        try:
            users = User.query.count()
            admins = Admin.query.count()
            orders = Order.query.count()
            addresses = Address.query.count()
            carts = Cart.query.count()
            
            print(f"✅ Users in database: {users}")
            print(f"✅ Admins in database: {admins}")
            print(f"✅ Orders in database: {orders}")
            print(f"✅ Addresses in database: {addresses}")
            print(f"✅ Carts in database: {carts}")
        except Exception as e:
            print(f"❌ Database check failed: {str(e)}")

def main():
    print("\n" + "🌐 TESTING FASHIONBRAND API ENDPOINTS 🌐".center(60))
    print("Testing all routes and API endpoints\n")
    
    test_public_routes()
    test_auth_routes()
    test_user_registration_flow()
    test_shop_page()
    test_api_endpoints()
    test_database_integrity()
    
    print("\n" + "="*60)
    print("✅ ENDPOINT TESTING COMPLETE")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
