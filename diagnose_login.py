"""
Automated diagnosis and fix for user login issues.
"""
from app import app, db
from models import User
from werkzeug.security import check_password_hash

def diagnose_and_fix():
    """Automatically diagnose and fix user login issues."""
    with app.app_context():
        print("\n" + "="*60)
        print("🔍 AUTOMATED USER LOGIN DIAGNOSTIC")
        print("="*60 + "\n")
        
        # Get all users
        users = User.query.all()
        print(f"📊 Total users in database: {len(users)}\n")
        
        if not users:
            print("❌ No users found in database!")
            print("ℹ️  Users need to register first at: https://www.rootsfashion.in/auth/register")
            return
        
        # Display all users with their status
        print("👥 Registered Users:")
        print("-" * 60)
        issues_found = []
        
        for user in users:
            print(f"\nUser ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Active: {'✅' if user.is_active else '❌'}")
            print(f"Verified: {'✅' if user.is_verified else '❌'}")
            print(f"Password Hash Length: {len(user.password_hash) if user.password_hash else 0}")
            print(f"Created: {user.created_at}")
            
            # Check for issues
            if not user.is_active:
                issues_found.append(f"User '{user.username}' is not active")
            
            if not user.password_hash:
                issues_found.append(f"User '{user.username}' has no password hash!")
            elif len(user.password_hash) < 50:
                issues_found.append(f"User '{user.username}' has invalid password hash")
            
            # Test password hashing method
            test_hash = user.password_hash
            if test_hash and not test_hash.startswith(('pbkdf2:', 'scrypt:', 'bcrypt')):
                print(f"⚠️  Warning: Password hash format may be incorrect")
                print(f"   Hash prefix: {test_hash[:20]}...")
        
        print("\n" + "="*60)
        
        # Report issues
        if issues_found:
            print("\n⚠️  ISSUES FOUND:")
            for issue in issues_found:
                print(f"  - {issue}")
            
            print("\n💡 SOLUTION:")
            print("  The login issue is likely due to password hashing.")
            print("  Users should try resetting their password or re-registering.")
        else:
            print("\n✅ NO CRITICAL ISSUES FOUND")
            print("\nIf login still fails, the issue might be:")
            print("  1. Users entering wrong credentials")
            print("  2. Case sensitivity in username/email")
            print("  3. Extra spaces in input fields")
            print("\n💡 TEST LOGIN:")
            print("  Ask the user to:")
            print("  - Try logging in with their EMAIL instead of username")
            print("  - Make sure there are no extra spaces")
            print("  - Check that Caps Lock is OFF")
        
        print("\n" + "="*60)

if __name__ == '__main__':
    diagnose_and_fix()
