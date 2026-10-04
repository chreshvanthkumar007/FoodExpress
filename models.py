from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user', 'admin'
    status = db.Column(db.String(20), default='active')  # 'active', 'inactive'
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('Cart', backref='user', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        # Supports Werkzeug hash verification with fallback for plain text if imported raw
        try:
            return check_password_hash(self.password, password)
        except Exception:
            return self.password == password
            
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cuisine = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    delivery_time = db.Column(db.String(50), nullable=False, default='30-40 mins')
    delivery_fee = db.Column(db.Numeric(10, 2), default=0.00)
    rating = db.Column(db.Numeric(2, 1), default=4.5)
    image = db.Column(db.String(255))
    status = db.Column(db.String(20), default='active')  # 'active', 'closed'
    
    # Relationships
    food_items = db.relationship('FoodItem', backref='restaurant', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    image = db.Column(db.String(255))
    
    # Relationships
    food_items = db.relationship('FoodItem', backref='category', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Category {self.name}>"


class FoodItem(db.Model):
    __tablename__ = 'food_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    ingredients = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    food_type = db.Column(db.String(20), nullable=False, default='veg')  # 'veg' or 'non-veg'
    image = db.Column(db.String(255))
    availability = db.Column(db.Boolean, default=True)  # True = Available, False = Unavailable
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    cart_items = db.relationship('Cart', backref='food_item', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='food_item', lazy=True, passive_deletes=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<FoodItem {self.name} - Rs.{self.price}>"


class Cart(db.Model):
    __tablename__ = 'cart'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('food_items.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'food_id', name='uq_user_food_cart'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def item_total(self):
        if not self.food_item or self.food_item.price is None:
            return 0.0
        return float(self.food_item.price) * (self.quantity or 1)

    def __repr__(self):
        return f"<Cart User:{self.user_id} Food:{self.food_id} Qty:{self.quantity}>"


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False, default='Cash on Delivery')
    order_status = db.Column(db.String(50), nullable=False, default='Order Placed')
    # Allowed: 'Order Placed', 'Accepted', 'Preparing', 'Out for Delivery', 'Delivered', 'Cancelled'
    order_date = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def formatted_id(self):
        return f"ORD#{self.id:04d}"

    def __repr__(self):
        return f"<Order {self.formatted_id} Status:{self.order_status}>"


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('food_items.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def item_total(self):
        if self.price is None:
            return 0.0
        return float(self.price) * (self.quantity or 1)

    def __repr__(self):
        return f"<OrderItem Order:{self.order_id} Food:{self.food_id} Qty:{self.quantity}>"


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<ContactMessage {self.name} - {self.email}>"
