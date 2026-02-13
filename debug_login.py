"""
Debug script to check and fix user login issues.
"""
from app import app, db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

def debug_user_login():
    """Debug user authentication issues."""
    with app.app_context():
        print("\n" + "="*60)
        print("USER LOGIN DEBUG TOOL")
        print("="*60 + "\n")
        
        # Get all users
        users = User.query.all()
        print(f"📊 Total users in database: {len(users)}\n")
        
        if not users:
            print("❌ No users found in database!")
            return
        
        # Display all users
        print("👥 Registered Users:")
        print("-" * 60)
        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Active: {user.is_active}")
            print(f"Password Hash: {user.password_hash[:50]}...")
            print("-" * 60)
        
        # Test login for each user
        print("\n🔐 Testing Login Functionality:")
        print("-" * 60)
        
        # Ask for test credentials
        test_username = input("\nEnter username to test login: ").strip()
        test_password = input("Enter password: ").strip()
        
        # Find user
        user = User.query.filter_by(username=test_username).first()
        if not user:
            user = User.query.filter_by(email=test_username).first()
        
        if not user:
            print(f"\n❌ User '{test_username}' not found in database!")
            return
        
        print(f"\n✅ User found: {user.username} ({user.email})")
        print(f"Active status: {user.is_active}")
        print(f"Password hash exists: {bool(user.password_hash)}")
        
        # Test password
        print("\n🔍 Testing password verification...")
        is_valid = user.check_password(test_password)
        
        if is_valid:
            print("✅ PASSWORD VALID - Login should work!")
        else:
            print("❌ PASSWORD INVALID - Login will fail!")
            
            # Offer to reset password
            reset = input("\nWould you like to reset this user's password? (yes/no): ").strip().lower()
            if reset == 'yes':
                new_password = input("Enter new password: ").strip()
                user.set_password(new_password)
                db.session.commit()
                print(f"\n✅ Password reset successful for user '{user.username}'!")
                print(f"New password: {new_password}")
                
                # Test again
                print("\n🔍 Testing new password...")
                if user.check_password(new_password):
                    print("✅ New password works! Login should now succeed.")
                else:
                    print("❌ Password reset failed! Manual intervention needed.")

if __name__ == '__main__':
    debug_user_login()
