"""
Repository layer for data access operations.
Implements Repository Pattern following SOLID principles.
"""
from typing import Optional, List
from models import db, User, Admin, Order, Address


class UserRepository:
    """Repository for User data access operations."""
    
    @staticmethod
    def create(email: str, username: str, password: str, **kwargs) -> User:
        """Create a new user."""
        user = User(email=email, username=username, **kwargs)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def find_by_id(user_id: int) -> Optional[User]:
        """Find user by ID."""
        return User.query.get(user_id)
    
    @staticmethod
    def find_by_email(email: str) -> Optional[User]:
        """Find user by email."""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_username(username: str) -> Optional[User]:
        """Find user by username."""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def find_all(page: int = 1, per_page: int = 20) -> List[User]:
        """Get all users with pagination."""
        return User.query.paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def update(user: User, **kwargs) -> User:
        """Update user information."""
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.session.commit()
        return user
    
    @staticmethod
    def delete(user: User) -> None:
        """Delete a user."""
        db.session.delete(user)
        db.session.commit()
    
    @staticmethod
    def email_exists(email: str) -> bool:
        """Check if email already exists."""
        return User.query.filter_by(email=email).first() is not None
    
    @staticmethod
    def username_exists(username: str) -> bool:
        """Check if username already exists."""
        return User.query.filter_by(username=username).first() is not None


class AdminRepository:
    """Repository for Admin data access operations."""
    
    @staticmethod
    def create(email: str, username: str, password: str, **kwargs) -> Admin:
        """Create a new admin."""
        admin = Admin(email=email, username=username, **kwargs)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        return admin
    
    @staticmethod
    def find_by_id(admin_id: int) -> Optional[Admin]:
        """Find admin by ID."""
        return Admin.query.get(admin_id)
    
    @staticmethod
    def find_by_email(email: str) -> Optional[Admin]:
        """Find admin by email."""
        return Admin.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_username(username: str) -> Optional[Admin]:
        """Find admin by username."""
        return Admin.query.filter_by(username=username).first()
    
    @staticmethod
    def find_all() -> List[Admin]:
        """Get all admins."""
        return Admin.query.all()
    
    @staticmethod
    def update(admin: Admin, **kwargs) -> Admin:
        """Update admin information."""
        for key, value in kwargs.items():
            if hasattr(admin, key):
                setattr(admin, key, value)
        db.session.commit()
        return admin
    
    @staticmethod
    def delete(admin: Admin) -> None:
        """Delete an admin."""
        db.session.delete(admin)
        db.session.commit()


class OrderRepository:
    """Repository for Order data access operations."""
    
    @staticmethod
    def create(user_id: int, total_amount: float, **kwargs) -> Order:
        """Create a new order."""
        import secrets
        order_number = f"ORD-{secrets.token_hex(8).upper()}"
        order = Order(
            order_number=order_number,
            user_id=user_id,
            total_amount=total_amount,
            **kwargs
        )
        db.session.add(order)
        db.session.commit()
        return order
    
    @staticmethod
    def find_by_id(order_id: int) -> Optional[Order]:
        """Find order by ID."""
        return Order.query.get(order_id)
    
    @staticmethod
    def find_by_order_number(order_number: str) -> Optional[Order]:
        """Find order by order number."""
        return Order.query.filter_by(order_number=order_number).first()
    
    @staticmethod
    def find_by_user(user_id: int, page: int = 1, per_page: int = 20):
        """Get all orders for a user."""
        return Order.query.filter_by(user_id=user_id).order_by(
            Order.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def find_all(page: int = 1, per_page: int = 20):
        """Get all orders with pagination."""
        return Order.query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def update_status(order: Order, status: str) -> Order:
        """Update order status."""
        order.status = status
        db.session.commit()
        return order


class AddressRepository:
    """Repository for Address data access operations."""
    
    @staticmethod
    def create(user_id: int, **kwargs) -> Address:
        """Create a new address."""
        address = Address(user_id=user_id, **kwargs)
        db.session.add(address)
        db.session.commit()
        return address
    
    @staticmethod
    def find_by_id(address_id: int) -> Optional[Address]:
        """Find address by ID."""
        return Address.query.get(address_id)
    
    @staticmethod
    def find_by_user(user_id: int) -> List[Address]:
        """Get all addresses for a user."""
        return Address.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def find_default(user_id: int) -> Optional[Address]:
        """Find default address for a user."""
        return Address.query.filter_by(user_id=user_id, is_default=True).first()
    
    @staticmethod
    def update(address: Address, **kwargs) -> Address:
        """Update address information."""
        for key, value in kwargs.items():
            if hasattr(address, key):
                setattr(address, key, value)
        db.session.commit()
        return address
    
    @staticmethod
    def delete(address: Address) -> None:
        """Delete an address."""
        db.session.delete(address)
        db.session.commit()
