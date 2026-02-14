"""SQLAlchemy database models for Retail Analytics Dashboard.

This module defines all database tables and relationships for the retail
analytics system including orders, products, customers, and categories.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional

from sqlalchemy import Index, CheckConstraint
from sqlalchemy.orm import validates
from database import db


logger = logging.getLogger(__name__)


# ==================== Base Model Mixin ====================

class TimestampMixin:
    """Mixin to add timestamp columns to models."""

    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class SerializerMixin:
    """Mixin to add serialization methods to models."""

    def to_dict(self, exclude: Optional[list] = None) -> Dict[str, Any]:
        """Convert model instance to dictionary.

        Args:
            exclude: List of column names to exclude from output.

        Returns:
            dict: Dictionary representation of the model.
        """
        exclude = exclude or []
        result = {}

        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)

                # Convert datetime objects to ISO format strings
                if isinstance(value, datetime):
                    value = value.isoformat()
                # Convert Decimal to float for JSON serialization
                elif isinstance(value, Decimal):
                    value = float(value)

                result[column.name] = value

        return result

    def __repr__(self) -> str:
        """String representation of model instance."""
        class_name = self.__class__.__name__
        return f"<{class_name} {self.id}>"


# ==================== Core Models ====================

class Customer(db.Model, TimestampMixin, SerializerMixin):
    """Customer model representing retail customers.

    Attributes:
        id: Unique customer identifier.
        email: Customer email address (unique).
        first_name: Customer first name.
        last_name: Customer last name.
        phone: Customer phone number.
        address: Customer street address.
        city: Customer city.
        state: Customer state/province.
        zip_code: Customer postal code.
        country: Customer country.
        customer_segment: Customer segment (e.g., VIP, Regular, New).
        lifetime_value: Total customer lifetime value.
        orders: Relationship to orders.
    """

    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(100), default='USA')
    customer_segment = db.Column(db.String(50), index=True)
    lifetime_value = db.Column(db.Numeric(12, 2), default=0.00)

    # Relationships
    orders = db.relationship(
        'Order', back_populates='customer', lazy='dynamic')

    # Indexes
    __table_args__ = (
        Index('idx_customer_name', 'last_name', 'first_name'),
        Index('idx_customer_location', 'city', 'state'),
    )

    @validates('email')
    def validate_email(self, key, email):
        """Validate email format."""
        if '@' not in email:
            raise ValueError("Invalid email address")
        return email.lower()

    @property
    def full_name(self) -> str:
        """Get customer full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def order_count(self) -> int:
        """Get total number of orders."""
        return self.orders.count()


class Category(db.Model, TimestampMixin, SerializerMixin):
    """Product category model.

    Attributes:
        id: Unique category identifier.
        name: Category name.
        description: Category description.
        parent_id: Parent category ID for hierarchical structure.
        products: Relationship to products.
    """

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    # Self-referential relationship for category hierarchy
    subcategories = db.relationship(
        'Category',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic'
    )

    # Relationship to products
    products = db.relationship(
        'Product', back_populates='category', lazy='dynamic')


class Product(db.Model, TimestampMixin, SerializerMixin):
    """Product model representing retail products.

    Attributes:
        id: Unique product identifier.
        sku: Stock keeping unit (unique).
        name: Product name.
        description: Product description.
        category_id: Foreign key to category.
        price: Product price.
        cost: Product cost.
        stock_quantity: Current stock level.
        reorder_level: Minimum stock level before reorder.
        is_active: Whether product is active for sale.
        category: Relationship to category.
        order_items: Relationship to order items.
    """

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    category_id = db.Column(
        db.Integer, db.ForeignKey('categories.id'),
        nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    cost = db.Column(db.Numeric(10, 2))
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    reorder_level = db.Column(db.Integer, default=10)
    is_active = db.Column(
        db.Boolean, default=True, nullable=False, index=True)

    # Relationships
    category = db.relationship('Category', back_populates='products')
    order_items = db.relationship(
        'OrderItem', back_populates='product', lazy='dynamic')

    # Constraints
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_positive'),
        CheckConstraint('cost >= 0', name='check_cost_positive'),
        CheckConstraint(
            'stock_quantity >= 0',
            name='check_stock_non_negative'),
    )

    @validates('price', 'cost')
    def validate_money(self, key, value):
        """Validate monetary values are positive."""
        if value is not None and value < 0:
            raise ValueError(f"{key} must be non-negative")
        return value

    @property
    def profit_margin(self) -> Optional[float]:
        """Calculate profit margin percentage."""
        if self.price and self.cost and self.price > 0:
            return float(((self.price - self.cost) / self.price) * 100)
        return None

    @property
    def needs_reorder(self) -> bool:
        """Check if product needs reordering."""
        return self.stock_quantity <= self.reorder_level


class Order(db.Model, TimestampMixin, SerializerMixin):
    """Order model representing customer orders.

    Attributes:
        id: Unique order identifier.
        order_number: Human-readable order number.
        customer_id: Foreign key to customer.
        order_date: Date order was placed.
        status: Order status.
        subtotal: Order subtotal before tax.
        tax_amount: Tax amount.
        shipping_cost: Shipping cost.
        total_amount: Total order amount.
        payment_method: Payment method used.
        shipping_address: Shipping address.
        notes: Order notes.
        customer: Relationship to customer.
        items: Relationship to order items.
    """

    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_number = db.Column(
        db.String(50), unique=True,
        nullable=False, index=True)
    customer_id = db.Column(
        db.Integer, db.ForeignKey('customers.id'),
        nullable=False)
    order_date = db.Column(
        db.DateTime, nullable=False,
        default=datetime.utcnow, index=True)
    status = db.Column(
        db.String(50),
        nullable=False,
        default='pending',
        index=True
    )
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    tax_amount = db.Column(db.Numeric(12, 2), default=0.00)
    shipping_cost = db.Column(db.Numeric(12, 2), default=0.00)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_method = db.Column(db.String(50))
    shipping_address = db.Column(db.Text)
    notes = db.Column(db.Text)

    # Relationships
    customer = db.relationship('Customer', back_populates='orders')
    items = db.relationship(
        'OrderItem',
        back_populates='order',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    # Indexes
    __table_args__ = (
        Index('idx_order_customer_date', 'customer_id', 'order_date'),
        Index('idx_order_status_date', 'status', 'order_date'),
        CheckConstraint('total_amount >= 0', name='check_total_positive'),
    )

    @validates('status')
    def validate_status(self, key, status):
        """Validate order status."""
        valid_statuses = [
            'pending', 'processing', 'shipped',
            'delivered', 'cancelled', 'refunded']
        if status not in valid_statuses:
            raise ValueError(
                "Invalid status. Must be one of: "
                f"{', '.join(valid_statuses)}")
        return status

    @property
    def item_count(self) -> int:
        """Get total number of items in order."""
        return self.items.count()

    def calculate_totals(self) -> None:
        """Calculate order totals from order items."""
        self.subtotal = sum(item.line_total for item in self.items)
        self.total_amount = (
            self.subtotal + self.tax_amount + self.shipping_cost)


class OrderItem(db.Model, TimestampMixin, SerializerMixin):
    """Order item model representing products in an order.

    Attributes:
        id: Unique order item identifier.
        order_id: Foreign key to order.
        product_id: Foreign key to product.
        quantity: Quantity ordered.
        unit_price: Price per unit at time of order.
        discount_amount: Discount applied to this item.
        line_total: Total for this line item.
        order: Relationship to order.
        product: Relationship to product.
    """

    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey('orders.id'),
        nullable=False)
    product_id = db.Column(
        db.Integer, db.ForeignKey('products.id'),
        nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), default=0.00)
    line_total = db.Column(db.Numeric(12, 2), nullable=False)

    # Relationships
    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product', back_populates='order_items')

    # Constraints
    __table_args__ = (
        Index('idx_order_item_order', 'order_id'),
        Index('idx_order_item_product', 'product_id'),
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint(
            'unit_price >= 0',
            name='check_unit_price_non_negative'),
        CheckConstraint(
            'line_total >= 0',
            name='check_line_total_non_negative'),
    )

    @validates('quantity')
    def validate_quantity(self, key, quantity):
        """Validate quantity is positive."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        return quantity

    def calculate_line_total(self) -> None:
        """Calculate line total from quantity, unit price, and discount."""
        self.line_total = (
            (self.quantity * self.unit_price)
            - self.discount_amount)
