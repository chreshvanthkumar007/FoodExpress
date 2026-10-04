import os
import unittest
from decimal import Decimal

# Configure SQLite for test suite
os.environ['USE_SQLITE'] = 'True'
from config import Config
Config.USE_SQLITE = True
Config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

from app import create_app
from models import db, User, Restaurant, Category, FoodItem, Order, OrderItem, ContactMessage
from init_db import seed_initial_data

class FoodExpressTestSuite(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            seed_initial_data()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_01_public_pages(self):
        """Test public endpoints return 200 OK."""
        endpoints = ['/', '/restaurants', '/restaurant/1', '/menu', '/food/1', '/about', '/contact', '/login', '/register', '/admin/login']
        for ep in endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 200, f"Failed on endpoint {ep}")

    def test_02_contact_submission(self):
        """Test contact form submission."""
        res = self.client.post('/contact', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '9998887776',
            'message': 'Testing message submission'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Thank you! Your message has been received', res.data)

    def test_03_user_registration_and_login(self):
        """Test registration, duplicate email check, and login."""
        # 1. Register new user
        res = self.client.post('/register', data={
            'name': 'Kavita Roy',
            'email': 'kavita@example.com',
            'phone': '+91 9888877777',
            'password': 'Password@123',
            'confirm_password': 'Password@123',
            'address': 'Sector 15, Vashi, Navi Mumbai'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Kavita', res.data)

        # Log out before attempting duplicate registration
        self.client.get('/logout')

        # 2. Duplicate registration check
        res_dup = self.client.post('/register', data={
            'name': 'Kavita Duplicate',
            'email': 'kavita@example.com',
            'phone': '+91 9888877777',
            'password': 'Password@123',
            'confirm_password': 'Password@123',
            'address': 'Sector 15, Vashi, Navi Mumbai'
        }, follow_redirects=True)
        self.assertIn(b'already exists', res_dup.data)

    def test_04_cart_and_order_flow(self):
        """Test complete ordering workflow from cart to checkout to order tracking."""
        # Log in as sample user Rahul
        login_res = self.client.post('/login', data={
            'email': 'rahul@example.com',
            'password': 'User@123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)

        # Add food item #1 to cart (Chicken Biryani)
        cart_res = self.client.post('/cart/add', json={'food_id': 1, 'quantity': 2})
        self.assertEqual(cart_res.status_code, 200)
        self.assertTrue(cart_res.get_json()['success'])

        # View Cart
        view_res = self.client.get('/cart')
        self.assertEqual(view_res.status_code, 200)
        self.assertIn(b'Hyderabadi Chicken Dum Biryani', view_res.data)

        # Checkout page
        chk_res = self.client.get('/checkout')
        self.assertEqual(chk_res.status_code, 200)

        # Place Order
        order_res = self.client.post('/place-order', data={
            'name': 'Rahul Sharma',
            'phone': '+91 9822012345',
            'delivery_address': 'Flat 402, Green Valley Apartments',
            'city': 'Bengaluru',
            'pincode': '560038',
            'instructions': 'Leave with security guard',
            'payment_method': 'Cash on Delivery'
        }, follow_redirects=True)
        self.assertEqual(order_res.status_code, 200)
        self.assertIn(b'Order Placed Successfully', order_res.data)

        # View user orders
        orders_list = self.client.get('/orders')
        self.assertEqual(orders_list.status_code, 200)

    def test_05_admin_portal_flow(self):
        """Test admin authentication, dashboard metrics, and status update."""
        # Log in as admin
        admin_login = self.client.post('/admin/login', data={
            'email': 'admin@foodexpress.com',
            'password': 'Admin@123'
        }, follow_redirects=True)
        self.assertEqual(admin_login.status_code, 200)
        self.assertIn(b'Operational Overview', admin_login.data)

        # Admin management pages
        for ep in ['/admin/restaurants', '/admin/food', '/admin/orders', '/admin/users', '/admin/messages']:
            r = self.client.get(ep)
            self.assertEqual(r.status_code, 200, f"Admin endpoint failed: {ep}")

        # Update order status
        status_res = self.client.post('/admin/order/status/1', data={
            'status': 'Out for Delivery'
        }, follow_redirects=True)
        self.assertEqual(status_res.status_code, 200)

    def test_06_order_cancellation(self):
        """Test user cancelling an order that is in 'Order Placed' status."""
        self.client.post('/login', data={'email': 'rahul@example.com', 'password': 'User@123'})
        self.client.post('/cart/add', json={'food_id': 1, 'quantity': 1})
        self.client.post('/place-order', data={
            'name': 'Rahul Sharma',
            'phone': '+91 9822012345',
            'delivery_address': 'Flat 402, Green Valley Apartments',
            'payment_method': 'Cash on Delivery'
        }, follow_redirects=True)

        with self.app.app_context():
            latest_order = Order.query.filter_by(order_status='Order Placed').order_by(Order.id.desc()).first()
            self.assertIsNotNone(latest_order)
            order_id = latest_order.id

        # Cancel order
        cancel_res = self.client.post(f'/order/cancel/{order_id}', follow_redirects=True)
        self.assertEqual(cancel_res.status_code, 200)
        self.assertIn(b'cancelled successfully', cancel_res.data)

        with self.app.app_context():
            cancelled_order = db.session.get(Order, order_id)
            self.assertEqual(cancelled_order.order_status, 'Cancelled')

    def test_07_profile_update_and_security(self):
        """Test profile info update and password change."""
        self.client.post('/login', data={'email': 'rahul@example.com', 'password': 'User@123'})

        # Update profile details
        update_res = self.client.post('/profile', data={
            'action': 'update_profile',
            'name': 'Rahul Updated',
            'phone': '+91 9999988888',
            'address': 'New Updated Address, Bengaluru'
        }, follow_redirects=True)
        self.assertEqual(update_res.status_code, 200)
        self.assertIn(b'profile details have been updated', update_res.data)

        # Change password
        pw_res = self.client.post('/profile', data={
            'action': 'change_password',
            'current_password': 'User@123',
            'new_password': 'NewPassword@123',
            'confirm_password': 'NewPassword@123'
        }, follow_redirects=True)
        self.assertEqual(pw_res.status_code, 200)
        self.assertIn(b'Password changed successfully', pw_res.data)

    def test_08_error_pages(self):
        """Test custom 404 page."""
        res_404 = self.client.get('/non_existent_page_url_123')
        self.assertEqual(res_404.status_code, 404)
        self.assertIn(b'Page Not Found', res_404.data)

    def test_09_safe_deletions_and_repr(self):
        """Test safe deletion protection for food items with orders and ASCII repr safety."""
        # Check __repr__ safety
        with self.app.app_context():
            food = FoodItem.query.first()
            self.assertIn('Rs.', repr(food))

        # Log in as admin
        self.client.post('/admin/login', data={'email': 'admin@foodexpress.com', 'password': 'Admin@123'}, follow_redirects=True)

        # Attempt to delete food #1 (which has order history)
        del_food_res = self.client.post('/admin/food/delete/1', follow_redirects=True)
        self.assertEqual(del_food_res.status_code, 200)
        self.assertIn(b'existing customer orders', del_food_res.data)

        # Verify food #1 was deactivated rather than causing IntegrityError
        with self.app.app_context():
            food1 = db.session.get(FoodItem, 1)
            self.assertIsNotNone(food1)
            self.assertFalse(food1.availability)

        # Attempt to delete restaurant #1 (which has order history)
        del_rest_res = self.client.post('/admin/restaurant/delete/1', follow_redirects=True)
        self.assertEqual(del_rest_res.status_code, 200)
        self.assertIn(b'referenced in past customer orders', del_rest_res.data)

    def test_10_cart_and_order_templates_defensive_rendering(self):
        """Test cart.html and order_details.html rendering across various statuses and data states."""
        self.client.post('/login', data={'email': 'rahul@example.com', 'password': 'User@123'})

        # Add item and view cart
        self.client.post('/cart/add', json={'food_id': 2, 'quantity': 2})
        cart_res = self.client.get('/cart')
        self.assertEqual(cart_res.status_code, 200)
        self.assertIn(b'Your Food Cart', cart_res.data)
        self.assertIn(b'Order Summary', cart_res.data)

        # Place order and check order details rendering
        place_res = self.client.post('/place-order', data={
            'name': 'Rahul Sharma',
            'phone': '+91 9822012345',
            'delivery_address': 'Flat 402, Green Valley Apartments',
            'city': 'Bengaluru',
            'pincode': '560038',
            'payment_method': 'Cash on Delivery'
        }, follow_redirects=True)
        self.assertEqual(place_res.status_code, 200)

        with self.app.app_context():
            user = User.query.filter_by(email='rahul@example.com').first()
            order = Order.query.filter_by(user_id=user.id).order_by(Order.id.desc()).first()
            self.assertIsNotNone(order)
            order_id = order.id

        # Verify order_details.html renders for each progression status
        statuses = ['Order Placed', 'Accepted', 'Preparing', 'Out for Delivery', 'Delivered', 'Cancelled']
        for st in statuses:
            with self.app.app_context():
                ord_obj = db.session.get(Order, order_id)
                ord_obj.order_status = st
                db.session.commit()

            detail_res = self.client.get(f'/order/{order_id}')
            self.assertEqual(detail_res.status_code, 200)
            self.assertIn(st.encode(), detail_res.data)

    def test_11_login_open_redirect_protection(self):
        """Test open redirect vulnerability protection in login route."""
        # Attempt malicious protocol-relative redirect
        res = self.client.post('/login', data={
            'email': 'rahul@example.com',
            'password': 'User@123',
            'next': '//evil.com/hack'
        })
        self.assertEqual(res.status_code, 302)
        self.assertNotEqual(res.headers.get('Location'), '//evil.com/hack')
        self.assertTrue(res.headers.get('Location').endswith('/'))

        # Safe internal redirect
        self.client.get('/logout')
        safe_res = self.client.post('/login', data={
            'email': 'rahul@example.com',
            'password': 'User@123',
            'next': '/menu'
        })
        self.assertEqual(safe_res.status_code, 302)
        self.assertTrue(safe_res.headers.get('Location').endswith('/menu'))

    def test_12_cart_input_validation(self):
        """Test defensive parsing for malformed cart addition and updates."""
        self.client.post('/login', data={'email': 'rahul@example.com', 'password': 'User@123'})

        # Malformed add
        bad_add = self.client.post('/cart/add', json={'food_id': 'invalid', 'quantity': 'abc'})
        self.assertEqual(bad_add.status_code, 400)

        # Negative quantity
        neg_add = self.client.post('/cart/add', json={'food_id': 1, 'quantity': -5})
        self.assertEqual(neg_add.status_code, 400)

        # Malformed update
        bad_update = self.client.post('/cart/update', json={'cart_id': 'bad', 'quantity': 2})
        self.assertEqual(bad_update.status_code, 400)

    def test_13_checkout_post_and_admin_foods_alias(self):
        """Test POST submission directly to /checkout and /admin/foods plural route alias."""
        # 1. Test /admin/foods alias
        self.client.post('/admin/login', data={'email': 'admin@foodexpress.com', 'password': 'Admin@123'}, follow_redirects=True)
        res = self.client.get('/admin/foods')
        self.assertEqual(res.status_code, 200)

        # 2. Test POST /checkout
        self.client.get('/logout')
        self.client.post('/login', data={'email': 'rahul@example.com', 'password': 'User@123'})
        self.client.post('/cart/add', json={'food_id': 1, 'quantity': 1})
        order_res = self.client.post('/checkout', data={
            'name': 'Rahul Sharma',
            'phone': '+91 9822012345',
            'delivery_address': 'Flat 402, Green Valley Apartments',
            'city': 'Bengaluru',
            'pincode': '560038',
            'instructions': 'Ring bell',
            'payment_method': 'Cash on Delivery'
        }, follow_redirects=True)
        self.assertEqual(order_res.status_code, 200)
        self.assertIn(b'Order Placed Successfully', order_res.data)


if __name__ == '__main__':
    unittest.main()


