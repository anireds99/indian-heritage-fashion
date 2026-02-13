"""
Database models for Fashion Brand application.
Follows SOLID principles with clear separation of concerns.
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User model for customer authentication and profile management."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    
    # Profile
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy='dynamic')
    addresses = db.relationship('Address', backref='user', lazy='dynamic')
    
    def set_password(self, password: str) -> None:
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Admin(db.Model):
    """Admin model for administrative access."""
    
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    
    # Admin levels
    role = db.Column(db.String(20), default='admin')  # admin, super_admin
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password: str) -> None:
        """Hash and set admin password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
    
    def is_super_admin(self) -> bool:
        """Check if admin has super admin privileges."""
        return self.role == 'super_admin'
    
    def to_dict(self) -> dict:
        """Convert admin to dictionary (excluding sensitive data)."""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<Admin {self.username}>'


class Address(db.Model):
    """Shipping address model."""
    
    __tablename__ = 'addresses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address_line1 = db.Column(db.String(200), nullable=False)
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False, default='India')
    
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Address {self.city}, {self.state}>'


class Order(db.Model):
    """Order model for purchase tracking."""
    
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Order details
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    
    # Shipping
    shipping_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'))
    shipping_address = db.relationship('Address', foreign_keys=[shipping_address_id])
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='dynamic')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'


class OrderItem(db.Model):
    """Order item model for individual products in an order."""
    
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    size = db.Column(db.String(10))
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'


class Cart(db.Model):
    """Shopping cart model."""
    
    __tablename__ = 'carts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100))  # For guest users
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    items = db.relationship('CartItem', backref='cart', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_total(self) -> float:
        """Calculate total cart amount."""
        return sum(item.get_subtotal() for item in self.items)
    
    def get_item_count(self) -> int:
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items)
    
    def __repr__(self):
        return f'<Cart {self.id}>'


class CartItem(db.Model):
    """Cart item model."""
    
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    product_image = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    size = db.Column(db.String(10), default='M')
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def get_subtotal(self) -> float:
        """Calculate item subtotal."""
        return self.price * self.quantity
    
    def __repr__(self):
        return f'<CartItem {self.product_name} x{self.quantity}>'


class Payment(db.Model):
    """Payment transaction model."""
    
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    
    payment_method = db.Column(db.String(20), nullable=False)  # cod, card, upi
    payment_status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    
    # Card payment details (encrypted in production)
    transaction_id = db.Column(db.String(100))
    card_last4 = db.Column(db.String(4))
    
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='INR')
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Payment {self.id} - {self.payment_method}>'
