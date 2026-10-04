import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for, 
    flash, session, jsonify, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, desc, func

from config import Config
from models import (
    db, User, Restaurant, Category, FoodItem, 
    Cart, Order, OrderItem, ContactMessage
)
from utils.helpers import (
    login_required, admin_required, get_cart_count, 
    calculate_cart_summary, get_status_step_info
)
from init_db import init_database

def _safe_float(val, default=0.0):
    try:
        if val is None or str(val).strip() == '':
            return default
        return float(val)
    except (ValueError, TypeError):
        return default

def _safe_int(val, default=0):
    try:
        if val is None or str(val).strip() == '':
            return default
        return int(val)
    except (ValueError, TypeError):
        return default

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable ProxyFix so redirects and links preserve HTTPS when accessed via public tunnels
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Initialize extensions
    db.init_app(app)

    # Enable CORS for public access
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        return response

    @app.before_request
    def handle_options_preflight():
        if request.method == 'OPTIONS':
            response = app.make_default_options_response()
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            return response

    # Inject global context into all templates
    @app.context_processor
    def inject_global_data():
        user = None
        user_id = None
        try:
            user_id = session.get('user_id')
        except Exception:
            user_id = None

        if user_id:
            try:
                user = db.session.get(User, user_id)
            except Exception:
                user = None
                
        return {
            'cart_count': get_cart_count(),
            'current_user': user,
            'now': datetime.now()
        }

    # -------------------------------------------------------------
    # Public & Customer Facing Routes
    # -------------------------------------------------------------

    @app.route('/')
    def index():
        """Home page with hero banner, categories, top restaurants, and trending food items."""
        categories = Category.query.all()
        popular_restaurants = Restaurant.query.filter_by(status='active').order_by(Restaurant.rating.desc()).limit(6).all()
        popular_foods = FoodItem.query.filter_by(availability=True).order_by(FoodItem.id.asc()).limit(8).all()
        return render_template(
            'index.html',
            categories=categories,
            popular_restaurants=popular_restaurants,
            popular_foods=popular_foods
        )

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration route with password hashing."""
        if 'user_id' in session:
            return redirect(url_for('index'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            phone = request.form.get('phone', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            address = request.form.get('address', '').strip()

            # Validations
            if not all([name, email, phone, password, address]):
                flash('Please fill in all required fields.', 'danger')
                return render_template('register.html')

            if password != confirm_password:
                flash('Passwords do not match. Please verify and try again.', 'danger')
                return render_template('register.html')

            if len(password) < 6:
                flash('Password must be at least 6 characters long.', 'danger')
                return render_template('register.html')

            # Check duplicate email
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('An account with this email address already exists. Please log in.', 'warning')
                return redirect(url_for('login'))

            try:
                new_user = User(
                    name=name,
                    email=email,
                    phone=phone,
                    password=generate_password_hash(password),
                    address=address,
                    role='user',
                    status='active'
                )
                db.session.add(new_user)
                db.session.commit()

                # Automatically log the user in
                session['user_id'] = new_user.id
                session['user_name'] = new_user.name
                session['user_email'] = new_user.email
                session['role'] = new_user.role

                flash(f'Welcome to FoodExpress, {new_user.name}! Your account has been created.', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred while creating your account: {e}', 'danger')
                return render_template('register.html')

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Customer and staff login route."""
        if 'user_id' in session:
            return redirect(url_for('index'))

        next_page = request.args.get('next')

        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            next_page = request.form.get('next') or next_page

            user = User.query.filter_by(email=email).first()

            if user and user.check_password(password):
                if user.status != 'active':
                    flash('Your account has been deactivated. Please contact support.', 'danger')
                    return render_template('login.html')

                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_email'] = user.email
                session['role'] = user.role

                flash(f'Welcome back, {user.name}!', 'success')
                if next_page and next_page.startswith('/') and not next_page.startswith('//'):
                    return redirect(next_page)
                if user.is_admin():
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('index'))
            else:
                flash('Invalid email address or password. Please try again.', 'danger')

        return render_template('login.html', next=next_page)

    @app.route('/logout')
    def logout():
        """Log out user and clear session."""
        session.clear()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('login'))

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        """View and edit user profile details, or change password."""
        user = db.session.get(User, session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for('login'))

        if request.method == 'POST':
            action = request.form.get('action')

            if action == 'update_profile':
                user.name = request.form.get('name', user.name).strip()
                user.phone = request.form.get('phone', user.phone).strip()
                user.address = request.form.get('address', user.address).strip()
                session['user_name'] = user.name
                db.session.commit()
                flash('Your profile details have been updated.', 'success')

            elif action == 'change_password':
                current_pw = request.form.get('current_password', '')
                new_pw = request.form.get('new_password', '')
                confirm_pw = request.form.get('confirm_password', '')

                if not user.check_password(current_pw):
                    flash('Incorrect current password.', 'danger')
                elif new_pw != confirm_pw:
                    flash('New passwords do not match.', 'danger')
                elif len(new_pw) < 6:
                    flash('New password must be at least 6 characters.', 'danger')
                else:
                    user.set_password(new_pw)
                    db.session.commit()
                    flash('Password changed successfully!', 'success')

            return redirect(url_for('profile'))

        return render_template('profile.html', user=user)

    @app.route('/restaurants')
    def restaurants():
        """Browse restaurants with search and cuisine filters."""
        query = request.args.get('q', '').strip()
        cuisine = request.args.get('cuisine', '').strip()

        stmt = Restaurant.query.filter_by(status='active')
        if query:
            stmt = stmt.filter(
                or_(
                    Restaurant.name.ilike(f'%{query}%'),
                    Restaurant.cuisine.ilike(f'%{query}%'),
                    Restaurant.location.ilike(f'%{query}%')
                )
            )
        if cuisine:
            stmt = stmt.filter(Restaurant.cuisine.ilike(f'%{cuisine}%'))

        all_restaurants = stmt.order_by(Restaurant.rating.desc()).all()
        return render_template('restaurants.html', restaurants=all_restaurants, search_query=query)

    @app.route('/restaurant/<int:restaurant_id>')
    def restaurant_detail(restaurant_id):
        """Restaurant details and available food catalog."""
        restaurant = db.get_or_404(Restaurant, restaurant_id)
        food_items = FoodItem.query.filter_by(restaurant_id=restaurant.id).order_by(FoodItem.availability.desc()).all()
        return render_template('restaurant_menu.html', restaurant=restaurant, food_items=food_items)

    @app.route('/food/<int:food_id>')
    def food_details(food_id):
        """Food item details page with ingredients, description, and related dishes."""
        food = db.get_or_404(FoodItem, food_id)
        related_foods = FoodItem.query.filter(
            FoodItem.category_id == food.category_id,
            FoodItem.id != food.id,
            FoodItem.availability == True
        ).limit(4).all()
        return render_template('food_details.html', food=food, related_foods=related_foods)

    @app.route('/menu')
    def menu():
        """Full food menu catalog with live filters and search."""
        q = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        restaurant_id = request.args.get('restaurant_id', '').strip()
        food_type = request.args.get('food_type', '').strip()
        price_range = request.args.get('price_range', '').strip()

        stmt = FoodItem.query

        if q:
            stmt = stmt.filter(
                or_(
                    FoodItem.name.ilike(f'%{q}%'),
                    FoodItem.description.ilike(f'%{q}%')
                )
            )

        if category:
            cat_obj = Category.query.filter_by(name=category).first()
            if cat_obj:
                stmt = stmt.filter(FoodItem.category_id == cat_obj.id)

        if restaurant_id and restaurant_id.isdigit():
            stmt = stmt.filter(FoodItem.restaurant_id == int(restaurant_id))

        if food_type in ('veg', 'non-veg'):
            stmt = stmt.filter(FoodItem.food_type == food_type)

        if price_range == 'under_150':
            stmt = stmt.filter(FoodItem.price < 150)
        elif price_range == '150_300':
            stmt = stmt.filter(FoodItem.price >= 150, FoodItem.price <= 300)
        elif price_range == 'above_300':
            stmt = stmt.filter(FoodItem.price > 300)

        food_items = stmt.order_by(FoodItem.availability.desc(), FoodItem.id.asc()).all()
        categories = Category.query.all()
        restaurants_list = Restaurant.query.filter_by(status='active').all()

        return render_template(
            'menu.html',
            food_items=food_items,
            categories=categories,
            restaurants=restaurants_list,
            selected_q=q,
            selected_category=category,
            selected_restaurant_id=restaurant_id,
            selected_type=food_type,
            selected_price=price_range
        )

    # -------------------------------------------------------------
    # Cart & Checkout Routes
    # -------------------------------------------------------------

    @app.route('/cart')
    def view_cart():
        """View user's shopping cart items and order breakdown."""
        if 'user_id' not in session:
            flash('Please log in to view and manage your shopping cart.', 'info')
            return redirect(url_for('login', next=request.path))

        user_id = session['user_id']
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        
        # Purge any orphaned cart items where food_item was removed from catalog
        valid_items = []
        orphaned_found = False
        for item in cart_items:
            if not item.food_item:
                db.session.delete(item)
                orphaned_found = True
            else:
                valid_items.append(item)
        if orphaned_found:
            db.session.commit()
            cart_items = valid_items

        summary = calculate_cart_summary(cart_items)
        return render_template('cart.html', cart_items=cart_items, summary=summary)

    @app.route('/cart/add', methods=['POST'])
    def cart_add():
        """Add item to shopping cart (AJAX / Form)."""
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Please log in first', 'redirect': url_for('login')}), 401
            flash('Please log in to add items to your cart.', 'warning')
            return redirect(url_for('login'))

        user_id = session['user_id']
        data = request.get_json(silent=True) or request.form

        food_id = _safe_int(data.get('food_id'))
        quantity = _safe_int(data.get('quantity', 1), default=1)

        if food_id <= 0 or quantity < 1:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Invalid item or quantity'}), 400
            flash('Invalid item or quantity.', 'warning')
            return redirect(request.referrer or url_for('menu'))

        food = db.session.get(FoodItem, food_id)
        if not food or not food.availability:
            if request.is_json:
                return jsonify({'success': False, 'message': 'This item is currently unavailable'}), 400
            flash('This item is currently unavailable.', 'warning')
            return redirect(request.referrer or url_for('menu'))

        cart_item = Cart.query.filter_by(user_id=user_id, food_id=food_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart(user_id=user_id, food_id=food_id, quantity=quantity)
            db.session.add(cart_item)

        db.session.commit()

        total_count = get_cart_count()

        if request.is_json:
            return jsonify({
                'success': True,
                'message': f'Added {food.name} to your cart!',
                'cart_count': total_count
            })

        flash(f'Added {food.name} to your cart!', 'success')
        return redirect(url_for('view_cart'))

    @app.route('/cart/update', methods=['POST'])
    @login_required
    def cart_update():
        """Update quantity of an item in the cart."""
        data = request.get_json(silent=True) or request.form
        cart_id = _safe_int(data.get('cart_id'))
        quantity = _safe_int(data.get('quantity', 1), default=1)

        if cart_id <= 0:
            return jsonify({'success': False, 'message': 'Invalid cart item'}), 400

        cart_item = Cart.query.filter_by(id=cart_id, user_id=session['user_id']).first()
        if not cart_item:
            return jsonify({'success': False, 'message': 'Cart item not found'}), 404

        if quantity <= 0:
            db.session.delete(cart_item)
        else:
            cart_item.quantity = quantity

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Cart updated',
            'cart_count': get_cart_count()
        })

    @app.route('/cart/remove/<int:cart_id>', methods=['POST', 'GET'])
    @login_required
    def cart_remove(cart_id):
        """Remove item from cart."""
        cart_item = Cart.query.filter_by(id=cart_id, user_id=session['user_id']).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            flash('Item removed from cart.', 'info')

        if request.is_json:
            return jsonify({'success': True, 'cart_count': get_cart_count()})
        return redirect(url_for('view_cart'))

    @app.route('/cart/clear', methods=['POST', 'GET'])
    @login_required
    def cart_clear():
        """Empty all items from cart."""
        Cart.query.filter_by(user_id=session['user_id']).delete()
        db.session.commit()
        flash('Your cart has been cleared.', 'info')
        if request.is_json:
            return jsonify({'success': True, 'cart_count': 0})
        return redirect(url_for('view_cart'))

    @app.route('/checkout', methods=['GET', 'POST'])
    @login_required
    def checkout():
        """Checkout screen with delivery details form and order summary."""
        if request.method == 'POST':
            return place_order()

        user = db.session.get(User, session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for('login'))

        cart_items = Cart.query.filter_by(user_id=user.id).all()
        valid_items = []
        orphaned_found = False
        for item in cart_items:
            if not item.food_item:
                db.session.delete(item)
                orphaned_found = True
            else:
                valid_items.append(item)
        if orphaned_found:
            db.session.commit()
            cart_items = valid_items

        if not cart_items:
            flash('Your cart is empty. Add items before checking out.', 'warning')
            return redirect(url_for('menu'))

        summary = calculate_cart_summary(cart_items)
        return render_template('checkout.html', user=user, cart_items=cart_items, summary=summary)

    @app.route('/place-order', methods=['POST'])
    @login_required
    def place_order():
        """Create order in MySQL, copy order items, and clear cart."""
        user_id = session['user_id']
        user = db.session.get(User, user_id)
        if not user:
            session.clear()
            return redirect(url_for('login'))

        cart_items = Cart.query.filter_by(user_id=user_id).all()
        valid_items = [item for item in cart_items if item.food_item]

        if not valid_items:
            flash('Your cart is empty. Please add items before placing an order.', 'warning')
            return redirect(url_for('menu'))

        # Check for any items marked as sold out / unavailable
        unavailable = [item.food_item.name for item in valid_items if not item.food_item.availability]
        if unavailable:
            flash(f"The following item(s) are currently sold out: {', '.join(unavailable)}. Please adjust your cart to proceed.", 'warning')
            return redirect(url_for('view_cart'))

        # Delivery form inputs
        name = request.form.get('name', user.name or '').strip()
        phone = request.form.get('phone', user.phone or '').strip()
        address = request.form.get('delivery_address', user.address or '').strip()
        city = request.form.get('city', 'Bengaluru').strip()
        pincode = request.form.get('pincode', '560038').strip()
        instructions = request.form.get('instructions', '').strip()
        payment_method = request.form.get('payment_method', 'Cash on Delivery')

        if not name or not phone or not address:
            flash('Please provide your name, contact phone number, and delivery address.', 'danger')
            return redirect(url_for('checkout'))

        full_address = f"{address}, {city} - {pincode}"
        if instructions:
            full_address += f" (Note: {instructions})"

        summary = calculate_cart_summary(valid_items)

        try:
            # 1. Create order
            new_order = Order(
                user_id=user_id,
                total_amount=summary['grand_total'],
                delivery_address=full_address,
                phone=phone,
                payment_method=payment_method,
                order_status='Order Placed'
            )
            db.session.add(new_order)
            db.session.flush()  # assign new_order.id

            # 2. Create order items snapshot
            for item in valid_items:
                order_item = OrderItem(
                    order_id=new_order.id,
                    food_id=item.food_id,
                    quantity=item.quantity or 1,
                    price=item.food_item.price if item.food_item.price is not None else 0.0
                )
                db.session.add(order_item)

            # 3. Clear shopping cart
            Cart.query.filter_by(user_id=user_id).delete()
            db.session.commit()

            flash('Order placed successfully!', 'success')
            return redirect(url_for('order_success', order_id=new_order.id))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while placing your order: {e}', 'danger')
            return redirect(url_for('checkout'))

    @app.route('/order-success/<int:order_id>')
    @login_required
    def order_success(order_id):
        """Order confirmation and unique Order ID presentation."""
        if session.get('role') == 'admin':
            order = db.get_or_404(Order, order_id)
        else:
            order = Order.query.filter_by(id=order_id, user_id=session['user_id']).first_or_404()
        return render_template('order_success.html', order=order)

    @app.route('/orders')
    @login_required
    def orders():
        """User's previous order history."""
        user_orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.order_date.desc()).all()
        return render_template('orders.html', orders=user_orders)

    @app.route('/order/<int:order_id>')
    @login_required
    def order_detail(order_id):
        """Order tracking page with live status progression."""
        user_id = session['user_id']
        user = db.session.get(User, user_id)
        if not user:
            session.clear()
            return redirect(url_for('login'))
        
        # Admin can view any order; user can only view their own
        if user.is_admin():
            order = db.get_or_404(Order, order_id)
        else:
            order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()

        step_info = get_status_step_info(order.order_status)
        return render_template('order_details.html', order=order, step_info=step_info)

    @app.route('/order/cancel/<int:order_id>', methods=['POST'])
    @login_required
    def cancel_order(order_id):
        """Allow customer to cancel their order if it is still in 'Order Placed' status."""
        order = db.get_or_404(Order, order_id)
        if order.user_id != session['user_id'] and session.get('role') != 'admin':
            abort(403)

        if order.order_status != 'Order Placed':
            flash('This order cannot be cancelled as kitchen preparation or delivery has already started.', 'warning')
        else:
            order.order_status = 'Cancelled'
            db.session.commit()
            flash(f'Order {order.formatted_id} has been cancelled successfully.', 'info')

        return redirect(url_for('order_detail', order_id=order.id))

    # -------------------------------------------------------------
    # Static & Support Pages
    # -------------------------------------------------------------

    @app.route('/about')
    def about():
        """About Us page explaining FoodExpress and 3-step ordering process."""
        return render_template('about.html')

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        """Contact Us page storing feedback and inquiries into MySQL."""
        user = db.session.get(User, session['user_id']) if 'user_id' in session else None

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            message = request.form.get('message', '').strip()

            if not all([name, email, message]):
                flash('Please complete all required fields.', 'danger')
            else:
                msg = ContactMessage(
                    name=name,
                    email=email,
                    phone=phone,
                    message=message
                )
                db.session.add(msg)
                db.session.commit()
                flash('Thank you! Your message has been received. Our team will get back to you shortly.', 'success')
                return redirect(url_for('contact'))

        return render_template('contact.html', user=user)

    # -------------------------------------------------------------
    # Administrator Portal Routes
    # -------------------------------------------------------------

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        """Dedicated Administrator Portal login."""
        if 'user_id' in session and session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))

        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password) and user.is_admin():
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_email'] = user.email
                session['role'] = user.role
                flash('Welcome to the FoodExpress Administration Console.', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid Administrator credentials or unauthorized account.', 'danger')

        return render_template('admin/login.html')

    @app.route('/admin/logout')
    def admin_logout():
        """Log out administrator."""
        session.clear()
        flash('Administrator signed out successfully.', 'info')
        return redirect(url_for('admin_login'))

    @app.route('/admin/dashboard')
    @admin_required
    def admin_dashboard():
        """Admin dashboard with 7 key metrics cards and quick actions."""
        total_users = User.query.filter_by(role='user').count()
        total_restaurants = Restaurant.query.count()
        total_foods = FoodItem.query.count()
        total_orders = Order.query.count()
        pending_orders = Order.query.filter(Order.order_status.in_(['Order Placed', 'Accepted', 'Preparing', 'Out for Delivery'])).count()
        delivered_orders = Order.query.filter_by(order_status='Delivered').count()

        revenue_res = db.session.query(func.sum(Order.total_amount)).filter(Order.order_status != 'Cancelled', Order.order_status != 'Rejected').scalar()
        total_revenue = float(revenue_res or 0.0)

        stats = {
            'total_users': total_users,
            'total_restaurants': total_restaurants,
            'total_foods': total_foods,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'total_revenue': total_revenue
        }

        recent_orders = Order.query.order_by(Order.order_date.desc()).limit(6).all()
        recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(4).all()

        return render_template(
            'admin/dashboard.html',
            stats=stats,
            recent_orders=recent_orders,
            recent_messages=recent_messages
        )

    # Admin Restaurant Management
    @app.route('/admin/restaurants')
    @admin_required
    def admin_restaurants():
        """List restaurants."""
        all_restaurants = Restaurant.query.order_by(Restaurant.id.desc()).all()
        return render_template('admin/restaurants.html', restaurants=all_restaurants)

    @app.route('/admin/restaurant/add', methods=['GET', 'POST'])
    @admin_required
    def admin_restaurant_add():
        """Add new restaurant partner."""
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            cuisine = request.form.get('cuisine', '').strip()
            description = request.form.get('description', '').strip()
            location = request.form.get('location', '').strip()
            delivery_time = request.form.get('delivery_time', '30-40 mins').strip()
            delivery_fee = max(0.0, _safe_float(request.form.get('delivery_fee'), 35.0))
            rating = max(1.0, min(5.0, _safe_float(request.form.get('rating'), 4.5)))
            image = request.form.get('image', 'restaurants/royal_biryani.svg').strip()
            status = request.form.get('status', 'active')

            if not name:
                flash('Restaurant name is required.', 'danger')
                return render_template('admin/restaurant_form.html', restaurant=None)

            rest = Restaurant(
                name=name,
                cuisine=cuisine,
                description=description,
                location=location,
                delivery_time=delivery_time,
                delivery_fee=delivery_fee,
                rating=rating,
                image=image,
                status=status
            )
            db.session.add(rest)
            db.session.commit()
            flash(f'Restaurant "{name}" added successfully!', 'success')
            return redirect(url_for('admin_restaurants'))

        return render_template('admin/restaurant_form.html', restaurant=None)

    @app.route('/admin/restaurant/edit/<int:restaurant_id>', methods=['GET', 'POST'])
    @admin_required
    def admin_restaurant_edit(restaurant_id):
        """Edit restaurant partner."""
        restaurant = db.get_or_404(Restaurant, restaurant_id)

        if request.method == 'POST':
            name = request.form.get('name', restaurant.name).strip()
            if not name:
                flash('Restaurant name cannot be empty.', 'danger')
                return render_template('admin/restaurant_form.html', restaurant=restaurant)

            restaurant.name = name
            restaurant.cuisine = request.form.get('cuisine', restaurant.cuisine).strip()
            restaurant.description = request.form.get('description', restaurant.description).strip()
            restaurant.location = request.form.get('location', restaurant.location).strip()
            restaurant.delivery_time = request.form.get('delivery_time', restaurant.delivery_time).strip()
            restaurant.delivery_fee = max(0.0, _safe_float(request.form.get('delivery_fee'), float(restaurant.delivery_fee or 0)))
            restaurant.rating = max(1.0, min(5.0, _safe_float(request.form.get('rating'), float(restaurant.rating or 4.5))))
            restaurant.image = request.form.get('image', restaurant.image).strip()
            restaurant.status = request.form.get('status', restaurant.status)

            db.session.commit()
            flash(f'Restaurant "{restaurant.name}" updated successfully!', 'success')
            return redirect(url_for('admin_restaurants'))

        return render_template('admin/restaurant_form.html', restaurant=restaurant)

    @app.route('/admin/restaurant/delete/<int:restaurant_id>', methods=['POST'])
    @admin_required
    def admin_restaurant_delete(restaurant_id):
        """Delete restaurant partner."""
        restaurant = db.get_or_404(Restaurant, restaurant_id)
        name = restaurant.name
        try:
            # Check if any food items of this restaurant are referenced in existing customer orders
            has_orders = any(item.order_items for item in restaurant.food_items)
            if has_orders:
                restaurant.status = 'closed'
                for item in restaurant.food_items:
                    item.availability = False
                db.session.commit()
                flash(f'Restaurant "{name}" is referenced in past customer orders. To preserve historical receipts, it has been marked as Closed and its dishes deactivated.', 'warning')
            else:
                db.session.delete(restaurant)
                db.session.commit()
                flash(f'Restaurant "{name}" and its associated dishes were deleted.', 'info')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while deleting restaurant: {e}', 'danger')
        return redirect(url_for('admin_restaurants'))

    # Admin Food Management
    @app.route('/admin/food')
    @app.route('/admin/foods')
    @admin_required
    def admin_food():
        """List food dishes."""
        foods = FoodItem.query.order_by(FoodItem.id.desc()).all()
        return render_template('admin/food_items.html', foods=foods)

    @app.route('/admin/food/add', methods=['GET', 'POST'])
    @admin_required
    def admin_food_add():
        """Add new food dish."""
        restaurants_list = Restaurant.query.filter_by(status='active').all()
        categories = Category.query.all()

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            restaurant_id = _safe_int(request.form.get('restaurant_id'))
            category_id = _safe_int(request.form.get('category_id'))
            price = _safe_float(request.form.get('price'), 0.0)
            food_type = request.form.get('food_type', 'veg')
            description = request.form.get('description', '').strip()
            ingredients = request.form.get('ingredients', '').strip()
            image = request.form.get('image', 'food/chicken_biryani.svg').strip()
            availability = request.form.get('availability', '1') == '1'

            if not name or restaurant_id <= 0 or category_id <= 0:
                flash('Please fill in all required dish information.', 'danger')
                return render_template('admin/food_form.html', food=None, restaurants=restaurants_list, categories=categories)

            if price <= 0:
                flash('Price must be greater than ₹0.00.', 'danger')
                return render_template('admin/food_form.html', food=None, restaurants=restaurants_list, categories=categories)

            food = FoodItem(
                name=name,
                restaurant_id=restaurant_id,
                category_id=category_id,
                price=price,
                food_type=food_type,
                description=description,
                ingredients=ingredients,
                image=image,
                availability=availability
            )
            db.session.add(food)
            db.session.commit()
            flash(f'Food item "{name}" created successfully!', 'success')
            return redirect(url_for('admin_food'))

        return render_template('admin/food_form.html', food=None, restaurants=restaurants_list, categories=categories)

    @app.route('/admin/food/edit/<int:food_id>', methods=['GET', 'POST'])
    @admin_required
    def admin_food_edit(food_id):
        """Edit food dish."""
        food = db.get_or_404(FoodItem, food_id)
        restaurants_list = Restaurant.query.all()
        categories = Category.query.all()

        if request.method == 'POST':
            food.name = request.form.get('name', food.name).strip()
            food.restaurant_id = _safe_int(request.form.get('restaurant_id'), food.restaurant_id)
            food.category_id = _safe_int(request.form.get('category_id'), food.category_id)
            food.price = max(0.0, _safe_float(request.form.get('price'), float(food.price or 0)))
            food.food_type = request.form.get('food_type', food.food_type)
            food.description = request.form.get('description', food.description).strip()
            food.ingredients = request.form.get('ingredients', food.ingredients).strip()
            food.image = request.form.get('image', food.image).strip()
            food.availability = request.form.get('availability', '1') == '1'

            db.session.commit()
            flash(f'Food item "{food.name}" updated successfully!', 'success')
            return redirect(url_for('admin_food'))

        return render_template('admin/food_form.html', food=food, restaurants=restaurants_list, categories=categories)

    @app.route('/admin/food/delete/<int:food_id>', methods=['POST'])
    @admin_required
    def admin_food_delete(food_id):
        """Delete food dish."""
        food = db.get_or_404(FoodItem, food_id)
        name = food.name
        try:
            # Check if this item is part of existing customer orders
            if food.order_items:
                food.availability = False
                db.session.commit()
                flash(f'Food item "{name}" is linked to existing customer orders. It has been deactivated (marked as Sold Out) to protect past customer receipts.', 'warning')
            else:
                db.session.delete(food)
                db.session.commit()
                flash(f'Food item "{name}" deleted from catalog.', 'info')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while deleting food item: {e}', 'danger')
        return redirect(url_for('admin_food'))

    @app.route('/admin/food/toggle/<int:food_id>', methods=['POST'])
    @admin_required
    def admin_food_toggle(food_id):
        """Quick toggle food availability."""
        food = db.get_or_404(FoodItem, food_id)
        food.availability = not food.availability
        db.session.commit()
        state = "Available" if food.availability else "Sold Out"
        flash(f'Marked "{food.name}" as {state}.', 'info')
        return redirect(url_for('admin_food'))

    # Admin Order Management
    @app.route('/admin/orders')
    @admin_required
    def admin_orders():
        """View all customer orders with status filter."""
        status = request.args.get('status', '').strip()
        stmt = Order.query
        if status:
            stmt = stmt.filter_by(order_status=status)
        all_orders = stmt.order_by(Order.order_date.desc()).all()
        return render_template('admin/orders.html', orders=all_orders, selected_status=status)

    @app.route('/admin/order/<int:order_id>')
    @admin_required
    def admin_order_detail(order_id):
        """View order details in admin portal."""
        order = db.get_or_404(Order, order_id)
        step_info = get_status_step_info(order.order_status)
        return render_template('admin/order_details.html', order=order, step_info=step_info)

    @app.route('/admin/order/status/<int:order_id>', methods=['POST'])
    @admin_required
    def admin_order_status(order_id):
        """Update order status in MySQL."""
        order = db.get_or_404(Order, order_id)
        new_status = request.form.get('status', '').strip()

        valid_statuses = ['Order Placed', 'Accepted', 'Preparing', 'Out for Delivery', 'Delivered', 'Rejected', 'Cancelled']
        if new_status in valid_statuses:
            order.order_status = new_status
            db.session.commit()
            flash(f'Order {order.formatted_id} updated to "{new_status}".', 'success')
        else:
            flash('Invalid order status.', 'danger')

        referrer = request.referrer
        if referrer and ('/admin/' in referrer or '/order' in referrer):
            return redirect(referrer)
        return redirect(url_for('admin_order_detail', order_id=order.id))

    # Admin User Management
    @app.route('/admin/users')
    @admin_required
    def admin_users():
        """View registered user directory."""
        users_list = User.query.order_by(User.id.desc()).all()
        return render_template('admin/users.html', users=users_list)

    @app.route('/admin/user/toggle/<int:user_id>', methods=['POST'])
    @admin_required
    def admin_user_toggle(user_id):
        """Activate or deactivate user account."""
        user = db.get_or_404(User, user_id)
        if user.id == session.get('user_id'):
            flash('Cannot modify your own administrative account status.', 'warning')
            return redirect(url_for('admin_users'))

        user.status = 'inactive' if user.status == 'active' else 'active'
        db.session.commit()
        flash(f'User "{user.name}" account status changed to {user.status.upper()}.', 'info')
        return redirect(url_for('admin_users'))

    # Admin Feedback & Contact Messages
    @app.route('/admin/messages')
    @admin_required
    def admin_messages():
        """View contact messages."""
        messages_list = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
        return render_template('admin/messages.html', messages=messages_list)

    @app.route('/admin/message/delete/<int:message_id>', methods=['POST'])
    @admin_required
    def admin_message_delete(message_id):
        """Delete customer inquiry message."""
        msg = db.get_or_404(ContactMessage, message_id)
        db.session.delete(msg)
        db.session.commit()
        flash('Message deleted.', 'info')
        return redirect(url_for('admin_messages'))

    # -------------------------------------------------------------
    # Error Handlers
    # -------------------------------------------------------------

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('404.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    return app


# Application entry point
app = create_app()

# Auto-initialize database on application startup (supports Gunicorn/WSGI production deployment)
if not app.config.get('TESTING'):
    try:
        init_database(app)
    except Exception as e:
        print(f"[!] Database startup check: {e}")

if __name__ == '__main__':
    print("[*] Starting FoodExpress Online Food Delivery System...")
    server_port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(host='0.0.0.0', port=server_port, debug=debug_mode)
