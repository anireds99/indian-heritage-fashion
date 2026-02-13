"""
Service layer for business logic operations.
Implements Service Pattern following SOLID principles.
"""
from typing import Optional, Dict, Any
from repositories import UserRepository, AdminRepository
from models import User, Admin


class AuthenticationService:
    """Service for authentication operations."""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.admin_repo = AdminRepository()
    
    def register_user(self, email: str, username: str, password: str, **kwargs) -> Dict[str, Any]:
        """
        Register a new user.
        Returns: {'success': bool, 'message': str, 'user': User (optional)}
        """
        # Validate email
        if self.user_repo.email_exists(email):
            return {'success': False, 'message': 'Email already registered'}
        
        # Validate username
        if self.user_repo.username_exists(username):
            return {'success': False, 'message': 'Username already taken'}
        
        # Validate password strength
        if len(password) < 6:
            return {'success': False, 'message': 'Password must be at least 6 characters'}
        
        try:
            user = self.user_repo.create(email, username, password, **kwargs)
            return {
                'success': True,
                'message': 'Registration successful',
                'user': user
            }
        except Exception as e:
            return {'success': False, 'message': f'Registration failed: {str(e)}'}
    
    def login_user(self, identifier: str, password: str) -> Dict[str, Any]:
        """
        Login user with email/username and password.
        Returns: {'success': bool, 'message': str, 'user': User (optional)}
        """
        # Try to find user by email or username
        user = self.user_repo.find_by_email(identifier)
        if not user:
            user = self.user_repo.find_by_username(identifier)
        
        if not user:
            return {'success': False, 'message': 'Invalid credentials'}
        
        if not user.is_active:
            return {'success': False, 'message': 'Account is deactivated'}
        
        if not user.check_password(password):
            return {'success': False, 'message': 'Invalid credentials'}
        
        user.update_last_login()
        
        return {
            'success': True,
            'message': 'Login successful',
            'user': user
        }
    
    def register_admin(self, email: str, username: str, password: str, **kwargs) -> Dict[str, Any]:
        """
        Register a new admin.
        Returns: {'success': bool, 'message': str, 'admin': Admin (optional)}
        """
        # Check if email exists
        if self.admin_repo.find_by_email(email):
            return {'success': False, 'message': 'Email already registered'}
        
        # Check if username exists
        if self.admin_repo.find_by_username(username):
            return {'success': False, 'message': 'Username already taken'}
        
        # Validate password strength
        if len(password) < 8:
            return {'success': False, 'message': 'Admin password must be at least 8 characters'}
        
        try:
            admin = self.admin_repo.create(email, username, password, **kwargs)
            return {
                'success': True,
                'message': 'Admin registration successful',
                'admin': admin
            }
        except Exception as e:
            return {'success': False, 'message': f'Registration failed: {str(e)}'}
    
    def login_admin(self, identifier: str, password: str) -> Dict[str, Any]:
        """
        Login admin with email/username and password.
        Returns: {'success': bool, 'message': str, 'admin': Admin (optional)}
        """
        # Try to find admin by email or username
        admin = self.admin_repo.find_by_email(identifier)
        if not admin:
            admin = self.admin_repo.find_by_username(identifier)
        
        if not admin:
            return {'success': False, 'message': 'Invalid admin credentials'}
        
        if not admin.is_active:
            return {'success': False, 'message': 'Admin account is deactivated'}
        
        if not admin.check_password(password):
            return {'success': False, 'message': 'Invalid admin credentials'}
        
        admin.update_last_login()
        
        return {
            'success': True,
            'message': 'Admin login successful',
            'admin': admin
        }


class UserService:
    """Service for user management operations."""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    def get_user_profile(self, user_id: int) -> Optional[User]:
        """Get user profile by ID."""
        return self.user_repo.find_by_id(user_id)
    
    def update_profile(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """Update user profile."""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        try:
            # Don't allow updating email/username through this method
            kwargs.pop('email', None)
            kwargs.pop('username', None)
            kwargs.pop('password_hash', None)
            
            updated_user = self.user_repo.update(user, **kwargs)
            return {
                'success': True,
                'message': 'Profile updated successfully',
                'user': updated_user
            }
        except Exception as e:
            return {'success': False, 'message': f'Update failed: {str(e)}'}
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password."""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        if not user.check_password(old_password):
            return {'success': False, 'message': 'Current password is incorrect'}
        
        if len(new_password) < 6:
            return {'success': False, 'message': 'New password must be at least 6 characters'}
        
        try:
            user.set_password(new_password)
            self.user_repo.update(user)
            return {'success': True, 'message': 'Password changed successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Password change failed: {str(e)}'}


class AdminService:
    """Service for admin operations."""
    
    def __init__(self):
        self.admin_repo = AdminRepository()
        self.user_repo = UserRepository()
    
    def get_all_users(self, page: int = 1, per_page: int = 20):
        """Get all users with pagination."""
        return self.user_repo.find_all(page, per_page)
    
    def get_all_admins(self):
        """Get all admins."""
        return self.admin_repo.find_all()
    
    def deactivate_user(self, user_id: int) -> Dict[str, Any]:
        """Deactivate a user account."""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        try:
            self.user_repo.update(user, is_active=False)
            return {'success': True, 'message': 'User deactivated successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Deactivation failed: {str(e)}'}
    
    def activate_user(self, user_id: int) -> Dict[str, Any]:
        """Activate a user account."""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        try:
            self.user_repo.update(user, is_active=True)
            return {'success': True, 'message': 'User activated successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Activation failed: {str(e)}'}
