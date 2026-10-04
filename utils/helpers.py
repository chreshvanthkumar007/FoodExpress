from functools import wraps
from flask import session, flash, redirect, url_for, request
from models import Cart

def login_required(f):
    """Decorator to protect routes requiring standard user authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to protect admin routes requiring admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in with an administrator account.', 'warning')
            return redirect(url_for('admin_login', next=request.path))
        if session.get('role') != 'admin':
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def get_cart_count():
    """Retrieve total quantity of items in current user's cart."""
    try:
        user_id = session.get('user_id')
    except Exception:
        return 0

    if not user_id:
        return 0
    try:
        items = Cart.query.filter_by(user_id=user_id).all()
        return sum(item.quantity for item in items if item)
    except Exception:
        return 0


def calculate_cart_summary(cart_items):
    """Calculate subtotal, delivery fee, taxes, and grand total."""
    subtotal = 0.0
    item_count = 0
    for item in (cart_items or []):
        if item and item.food_item:
            try:
                subtotal += float(item.food_item.price) * item.quantity
                item_count += item.quantity
            except (ValueError, TypeError):
                continue
    
    # Free delivery on orders over ₹499, otherwise flat ₹40 delivery fee
    delivery_fee = 0.0 if (subtotal >= 499.0 or subtotal == 0) else 40.0
    
    # 5% GST tax calculation
    tax = round(subtotal * 0.05, 2)
    grand_total = round(subtotal + delivery_fee + tax, 2)
    
    return {
        'subtotal': round(subtotal, 2),
        'delivery_fee': round(delivery_fee, 2),
        'tax': tax,
        'grand_total': grand_total,
        'item_count': item_count,
        'free_delivery_threshold': 499.0,
        'free_delivery_qualified': subtotal >= 499.0
    }


def get_status_step_info(order_status):
    """Return step index (0-4) and metadata for tracking order status progression."""
    order_status = str(order_status or 'Order Placed').strip()
    status_flow = ['Order Placed', 'Accepted', 'Preparing', 'Out for Delivery', 'Delivered']
    
    if order_status in ('Cancelled', 'Rejected'):
        return {
            'step_index': -1,
            'is_cancelled': True,
            'status_label': order_status,
            'badge_class': 'bg-danger'
        }
    
    try:
        idx = status_flow.index(order_status)
    except ValueError:
        idx = 0
        
    badge_map = {
        'Order Placed': 'bg-secondary',
        'Accepted': 'bg-info',
        'Preparing': 'bg-warning text-dark',
        'Out for Delivery': 'bg-primary',
        'Delivered': 'bg-success'
    }
    
    return {
        'step_index': idx,
        'is_cancelled': False,
        'status_label': order_status,
        'badge_class': badge_map.get(order_status, 'bg-primary')
    }
