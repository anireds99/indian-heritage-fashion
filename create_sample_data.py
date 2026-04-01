"""
Create sample data for testing admin panel and features
"""
import sys
sys.path.insert(0, '/Users/anirudhdev/FashionBrand')

from app import app, db
from models import User, Admin, Order, OrderItem, Address, Cart, CartItem, Payment
from repositories import UserRepository, AddressRepository, OrderRepository, PaymentRepository
from datetime import datetime, timedelta, timezone

def create_sample_users():
    """Create sample users for testing"""
    print("\n" + "="*50)
    print("Creating Sample Users")
    print("="*50)
    
    with app.app_context():
        users_data = [
            {
                'email': 'john@example.com',
                'username': 'john_doe',
                'password': 'Password123',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+91-98765-43210'
            },
            {
                'email': 'priya@example.com',
                'username': 'priya_sharma',
                'password': 'Password123',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'phone': '+91-97654-32109'
            },
            {
                'email': 'rahul@example.com',
                'username': 'rahul_kumar',
                'password': 'Password123',
                'first_name': 'Rahul',
                'last_name': 'Kumar',
                'phone': '+91-96543-21098'
            }
        ]
        
        for user_data in users_data:
            try:
                existing = UserRepository.find_by_email(user_data['email'])
                if not existing:
                    user = UserRepository.create(**user_data)
                    print(f"✅ Created user: {user.username}")
                else:
                    print(f"⚠️ User already exists: {user_data['username']}")
            except Exception as e:
                print(f"❌ Error creating user {user_data['username']}: {str(e)}")

def create_sample_addresses():
    """Create sample addresses for users"""
    print("\n" + "="*50)
    print("Creating Sample Addresses")
    print("="*50)
    
    with app.app_context():
        users = User.query.filter(User.username != 'testuser').all()
        
        addresses_data = [
            {
                'full_name': 'John Doe',
                'phone': '+91-98765-43210',
                'address_line1': '123 Main Street',
                'address_line2': 'Apt 4B',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'postal_code': '400001',
                'country': 'India',
                'is_default': True
            },
            {
                'full_name': 'Priya Sharma',
                'phone': '+91-97654-32109',
                'address_line1': '456 Park Lane',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'postal_code': '560001',
                'country': 'India',
                'is_default': True
            },
            {
                'full_name': 'Rahul Kumar',
                'phone': '+91-96543-21098',
                'address_line1': '789 Tech Avenue',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'postal_code': '500001',
                'country': 'India',
                'is_default': True
            }
        ]
        
        for i, user in enumerate(users):
            if i < len(addresses_data):
                try:
                    existing = AddressRepository.find_by_user(user.id)
                    if not existing:
                        address = AddressRepository.create(user_id=user.id, **addresses_data[i])
                        print(f"✅ Created address for {user.username} in {address.city}")
                    else:
                        print(f"⚠️ Address already exists for {user.username}")
                except Exception as e:
                    print(f"❌ Error creating address for {user.username}: {str(e)}")

def create_sample_orders():
    """Create sample orders for testing"""
    print("\n" + "="*50)
    print("Creating Sample Orders")
    print("="*50)
    
    with app.app_context():
        users = User.query.filter(User.username != 'testuser').all()
        
        products = [
            {'id': 1, 'name': 'Tanjore Temple Graphic Tee', 'price': 1299.99},
            {'id': 2, 'name': 'ISRO Space Missions Hoodie', 'price': 1999.99},
            {'id': 3, 'name': 'Hampi Ruins Heritage Tee', 'price': 1399.99},
            {'id': 4, 'name': 'Mysore Palace Heritage Tee', 'price': 1499.99},
        ]
        
        statuses = ['pending', 'confirmed', 'shipped', 'delivered']
        
        for idx, user in enumerate(users):
            try:
                address = AddressRepository.find_by_user(user.id)
                if address:
                    # Create order
                    order = OrderRepository.create(
                        user_id=user.id,
                        total_amount=products[idx]['price'] * 2,
                        shipping_address_id=address[0].id,
                        status=statuses[idx % len(statuses)]
                    )
                    
                    # Create order items
                    for i in range(2):
                        product = products[(idx + i) % len(products)]
                        item = OrderItem(
                            order_id=order.id,
                            product_id=product['id'],
                            product_name=product['name'],
                            quantity=1,
                            price=product['price'],
                            size='M'
                        )
                        db.session.add(item)
                    
                    # Create payment
                    payment = PaymentRepository.create(
                        order_id=order.id,
                        payment_method='cod',
                        amount=order.total_amount
                    )
                    
                    db.session.commit()
                    print(f"✅ Created order {order.order_number} for {user.username} (Status: {order.status})")
                else:
                    print(f"⚠️ No address found for {user.username}")
            except Exception as e:
                print(f"❌ Error creating order for {user.username}: {str(e)}")
                db.session.rollback()

def main():
    """Run all sample data creation"""
    print("\n" + "📊 CREATING SAMPLE DATA 📊".center(50))
    
    create_sample_users()
    create_sample_addresses()
    create_sample_orders()
    
    # Print summary
    print("\n" + "="*50)
    print("SAMPLE DATA SUMMARY")
    print("="*50)
    
    with app.app_context():
        user_count = User.query.count()
        admin_count = Admin.query.count()
        order_count = Order.query.count()
        address_count = Address.query.count()
        
        print(f"✅ Total Users: {user_count}")
        print(f"✅ Total Admins: {admin_count}")
        print(f"✅ Total Orders: {order_count}")
        print(f"✅ Total Addresses: {address_count}")
    
    print("="*50 + "\n")

if __name__ == '__main__':
    main()
