import os
import sys
from config import Config
from models import db, User, Restaurant, Category, FoodItem, Order, OrderItem, ContactMessage
from werkzeug.security import generate_password_hash

def init_database(app):
    """Initialize database tables and seed sample data if empty."""
    with app.app_context():
        # Test connection or create database in MySQL if using pymysql
        if not Config.USE_SQLITE:
            import pymysql
            try:
                conn = pymysql.connect(
                    host=Config.DB_HOST,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    port=int(Config.DB_PORT),
                    connect_timeout=3
                )
                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                conn.commit()
                conn.close()
                print(f"[*] Verified MySQL database '{Config.DB_NAME}'.")
            except Exception as e:
                print(f"[!] Warning: Could not connect to MySQL server at {Config.DB_HOST}:{Config.DB_PORT}: {e}")
                print("[*] Automatically falling back to local SQLite database (food_express.db) for demo/evaluation mode...")
                basedir = os.path.abspath(os.path.dirname(__file__))
                sqlite_uri = f"sqlite:///{os.path.join(basedir, 'food_express.db')}"
                app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
                app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
                Config.USE_SQLITE = True
                Config.SQLALCHEMY_DATABASE_URI = sqlite_uri

                # Rebind Flask-SQLAlchemy 3.x engine so subsequent queries use SQLite
                if hasattr(db, '_app_engines') and app in db._app_engines:
                    for eng in db._app_engines[app].values():
                        try:
                            eng.dispose()
                        except Exception:
                            pass
                    db._app_engines[app].clear()
                    options = {'url': sqlite_uri, 'echo': False, 'echo_pool': False}
                    if hasattr(db, '_apply_driver_defaults'):
                        db._apply_driver_defaults(options, app)
                    if hasattr(db, '_make_engine'):
                        db._app_engines[app][None] = db._make_engine(None, options, app)

        try:
            db.create_all()
            print("[*] Database tables created/verified successfully.")
            
            # Check if admin user exists, if not seed initial data
            if not User.query.filter_by(role='admin').first():
                seed_initial_data()
                print("[*] Initial sample data seeded successfully.")
            return True
        except Exception as e:
            print(f"[!] Error creating tables or seeding data: {e}")
            return False


def seed_initial_data():
    """Populate database with sample categories, restaurants, food, users, orders, and messages."""
    # 1. Users
    admin = User(
        name='Administrator',
        email='admin@foodexpress.com',
        phone='+91 9876543210',
        password=generate_password_hash('Admin@123'),
        address='FoodExpress Corporate Tower, MG Road, Bengaluru',
        role='admin',
        status='active'
    )
    user1 = User(
        name='Rahul Sharma',
        email='rahul@example.com',
        phone='+91 9822012345',
        password=generate_password_hash('User@123'),
        address='Flat 402, Green Valley Apartments, 12th Main Indiranagar, Bengaluru - 560038',
        role='user',
        status='active'
    )
    user2 = User(
        name='Priya Patel',
        email='priya@example.com',
        phone='+91 9876598765',
        password=generate_password_hash('User@123'),
        address='Bungalow 7, Lotus Enclave, Near Kothrud Stand, Pune - 411038',
        role='user',
        status='active'
    )
    db.session.add_all([admin, user1, user2])
    db.session.commit()

    # 2. Categories
    cat_names = [
        ('Biryani', 'categories/biryani.svg'),
        ('Pizza', 'categories/pizza.svg'),
        ('Burger', 'categories/burger.svg'),
        ('South Indian', 'categories/south_indian.svg'),
        ('North Indian', 'categories/north_indian.svg'),
        ('Chinese', 'categories/chinese.svg'),
        ('Desserts', 'categories/desserts.svg'),
        ('Beverages', 'categories/beverages.svg')
    ]
    categories = {}
    for name, img in cat_names:
        c = Category(name=name, image=img)
        db.session.add(c)
        categories[name] = c
    db.session.commit()

    # 3. Restaurants
    rest_data = [
        Restaurant(
            name='Royal Biryani House',
            description='Authentic slow-cooked Dum Biryanis, aromatic kebabs, and royal Mughlai gravies prepared with age-old secret spices.',
            cuisine='Biryani, Mughlai, Kebabs',
            location='100 Feet Rd, Indiranagar, Bengaluru',
            delivery_time='25-35 mins',
            delivery_fee=40.00,
            rating=4.8,
            image='restaurants/royal_biryani.svg',
            status='active'
        ),
        Restaurant(
            name='Pizza Paradiso',
            description='Handcrafted stone-oven Italian artisanal pizzas made with fresh mozzarella, sourdough crust, and imported herbs.',
            cuisine='Italian, Pizza, Fast Food',
            location='5th Block, Koramangala, Bengaluru',
            delivery_time='30-40 mins',
            delivery_fee=35.00,
            rating=4.6,
            image='restaurants/pizza_paradiso.svg',
            status='active'
        ),
        Restaurant(
            name='Burger Junction',
            description='Juicy grilled gourmet burgers, loaded seasoned peri-peri fries, and thick American style handcrafted milkshakes.',
            cuisine='Burgers, American, Fast Food',
            location='Brigade Road, MG Road, Bengaluru',
            delivery_time='20-30 mins',
            delivery_fee=30.00,
            rating=4.5,
            image='restaurants/burger_junction.svg',
            status='active'
        ),
        Restaurant(
            name='Spice Symphony',
            description='Rich North Indian curries, melting butter paneer, tender tandoori dishes, and freshly baked clay-oven breads.',
            cuisine='North Indian, Mughlai, Tandoor',
            location='Sector 2, HSR Layout, Bengaluru',
            delivery_time='35-45 mins',
            delivery_fee=45.00,
            rating=4.7,
            image='restaurants/spice_symphony.svg',
            status='active'
        ),
        Restaurant(
            name='Dakshin Flavors',
            description='Traditional South Indian crispy ghee dosas, fluffy steamed idlis, spicy vadas, and authentic filter coffee.',
            cuisine='South Indian, Chettinad, Dosa',
            location='4th Block, Jayanagar, Bengaluru',
            delivery_time='20-25 mins',
            delivery_fee=25.00,
            rating=4.6,
            image='restaurants/dakshin_flavors.svg',
            status='active'
        ),
        Restaurant(
            name='Dragon Wok',
            description='Sizzling Asian delicacies, Schezwan fried rice, spicy hakka noodles, steamed dim sums, and wok-tossed bowls.',
            cuisine='Chinese, Asian, Pan-Asian',
            location='ITPL Main Rd, Whitefield, Bengaluru',
            delivery_time='30-40 mins',
            delivery_fee=40.00,
            rating=4.4,
            image='restaurants/dragon_wok.svg',
            status='active'
        ),
        Restaurant(
            name='Sweet Tooth Cafe',
            description='Heavenly handcrafted desserts, traditional warm Indian sweets with rabri, artisanal ice creams, and refreshing coolers.',
            cuisine='Desserts, Bakery, Beverages',
            location='Church Street, Central Bengaluru',
            delivery_time='15-25 mins',
            delivery_fee=30.00,
            rating=4.9,
            image='restaurants/sweet_tooth.svg',
            status='active'
        )
    ]
    db.session.add_all(rest_data)
    db.session.commit()

    # 4. Food Items
    foods = [
        FoodItem(
            restaurant_id=rest_data[0].id, category_id=categories['Biryani'].id,
            name='Hyderabadi Chicken Dum Biryani',
            description='Aromatic long-grain basmati rice layered with succulent spiced chicken cuts, slow-cooked in handi seal with saffron & ghee.',
            ingredients='Basmati Rice, Marinated Chicken, Saffron, Ghee, Mint, Fried Onions, Spices',
            price=349.00, food_type='non-veg', image='food/chicken_biryani.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[0].id, category_id=categories['Biryani'].id,
            name='Royal Veg Dum Biryani',
            description='Fragrant basmati rice cooked on dum with seasonal garden vegetables, paneer cubes, cashews, and aromatic spices.',
            ingredients='Basmati Rice, Paneer, Carrots, Green Peas, Cashews, Saffron, Spices',
            price=269.00, food_type='veg', image='food/veg_biryani.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[0].id, category_id=categories['North Indian'].id,
            name='Mutton Galouti Kebab',
            description='Melt-in-mouth tender minced lamb kebabs marinated with raw papaya and 32 Awadhi secret spices, shallow fried in desi ghee.',
            ingredients='Minced Mutton, Raw Papaya, Awadhi Spices, Desi Ghee, Kewra Essence',
            price=399.00, food_type='non-veg', image='food/kebab.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[1].id, category_id=categories['Pizza'].id,
            name='Farmhouse Supreme Pizza',
            description='Classic 10-inch hand-stretched crust topped with rich herb marinara, golden corn, bell peppers, button mushrooms, and melted mozzarella.',
            ingredients='Pizza Dough, Tomato Marinara, Mozzarella, Bell Peppers, Mushrooms, Sweet Corn, Olives',
            price=389.00, food_type='veg', image='food/veg_pizza.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[1].id, category_id=categories['Pizza'].id,
            name='Peri Peri Chicken Feast Pizza',
            description='Spicy grilled peri-peri chicken chunks, roasted paprika, jalapenos, and smoked gouda on a thin crispy crust.',
            ingredients='Pizza Dough, Marinara, Peri Peri Chicken, Smoked Gouda, Jalapenos, Red Paprika',
            price=449.00, food_type='non-veg', image='food/chicken_pizza.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[1].id, category_id=categories['Pizza'].id,
            name='Cheesy Garlic Breadsticks',
            description='Freshly baked buttery breadsticks infused with roasted garlic, herbs, and loaded with stretchy mozzarella cheese.',
            ingredients='Bread Dough, Roasted Garlic Butter, Herbs, Mozzarella, Oregano Dip',
            price=149.00, food_type='veg', image='food/garlic_bread.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[2].id, category_id=categories['Burger'].id,
            name='Crispy Double Decker Chicken Burger',
            description='Crispy spiced chicken fillet topped with melted cheddar, fresh iceberg lettuce, sliced tomatoes, and creamy signature burger mayo.',
            ingredients='Sesame Brioche Bun, Fried Chicken Fillet, Cheddar Cheese, Pickles, Signature Sauce',
            price=229.00, food_type='non-veg', image='food/chicken_burger.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[2].id, category_id=categories['Burger'].id,
            name='Classic Veg Crunchy Cheese Burger',
            description='Golden crispy vegetable patty stuffed with cheese, lettuce, pickled gherkins, and tangy Thousand Island dressing in a toasted brioche.',
            ingredients='Brioche Bun, Crispy Veg Patty, Sliced Cheddar, Iceberg Lettuce, Thousand Island Sauce',
            price=169.00, food_type='veg', image='food/veg_burger.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[2].id, category_id=categories['Burger'].id,
            name='Loaded Peri Peri Fries',
            description='Crispy golden potato fries generously tossed in spicy African bird eye peri-peri seasoning and drizzled with warm cheese sauce.',
            ingredients='Potatoes, Peri Peri Seasoning, Warm Cheddar Drizzle, Fresh Herbs',
            price=129.00, food_type='veg', image='food/fries.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[3].id, category_id=categories['North Indian'].id,
            name='Paneer Butter Masala',
            description='Fresh cottage cheese cubes gently simmered in a velvety, rich tomato-cashew gravy finished with butter, cream, and kasuri methi.',
            ingredients='Cottage Cheese (Paneer), Tomatoes, Cashew Paste, Butter, Heavy Cream, Kasuri Methi',
            price=289.00, food_type='veg', image='food/paneer_butter_masala.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[3].id, category_id=categories['North Indian'].id,
            name='Butter Garlic Naan',
            description='Soft and bubbly traditional clay-tandoor flatbread brushed with crushed garlic and abundant salted melted butter.',
            ingredients='Refined Flour, Crushed Garlic, Salted Butter, Fresh Coriander, Nigella Seeds',
            price=55.00, food_type='veg', image='food/butter_naan.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[3].id, category_id=categories['North Indian'].id,
            name='Murgh Makhani Butter Chicken',
            description='Tender boneless chicken tikka cooked in an iconic smooth makhani tomato butter gravy with aromatic garam masala.',
            ingredients='Chicken Tikka, Tomatoes, Butter, Fresh Cream, Ginger-Garlic, Fenugreek',
            price=369.00, food_type='non-veg', image='food/butter_chicken.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[4].id, category_id=categories['South Indian'].id,
            name='Ghee Roast Masala Dosa',
            description='Ultra-crispy fermented rice-lentil crepe roasted in pure golden ghee, filled with spiced potato masala, served with 3 chutneys & sambar.',
            ingredients='Fermented Rice Batter, Pure Ghee, Spiced Potato Filling, Coconut Chutney, Sambar',
            price=139.00, food_type='veg', image='food/masala_dosa.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[4].id, category_id=categories['South Indian'].id,
            name='Steamed Idli & Medu Vada Combo',
            description='Two pillow-soft steamed rice idlis and one crispy medu vada served piping hot with fresh coconut chutney and spicy lentil sambar.',
            ingredients='Rice, Urad Dal, Curry Leaves, Mustard Seeds, Coconut, Tamarind Sambar',
            price=119.00, food_type='veg', image='food/idli_vada.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[5].id, category_id=categories['Chinese'].id,
            name='Schezwan Egg Fried Rice',
            description='Aromatic wok-tossed basmati rice with scrambled eggs, crunchy spring onions, shredded carrots, and fiery home-made Schezwan sauce.',
            ingredients='Basmati Rice, Fresh Eggs, Schezwan Sauce, Spring Onions, Garlic, Soy Sauce',
            price=219.00, food_type='non-veg', image='food/fried_rice.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[5].id, category_id=categories['Chinese'].id,
            name='Veg Hakka Noodles',
            description='Classic street-style stir-fried thin noodles tossed with crunchy cabbage, julienned capsicum, bean sprouts, and dark soy sauce.',
            ingredients='Noodles, Cabbage, Capsicum, Carrots, Spring Onions, Dark Soy, White Pepper',
            price=189.00, food_type='veg', image='food/hakka_noodles.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[6].id, category_id=categories['Desserts'].id,
            name='Warm Gulab Jamun with Rabri',
            description='Two traditional melt-in-mouth fried milk dough dumplings soaked in rose-cardamom sugar syrup, served with creamy thickened rabri.',
            ingredients='Khoya, Rose Sugar Syrup, Green Cardamom, Thickened Rabri, Pistachios',
            price=129.00, food_type='veg', image='food/gulab_jamun.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[6].id, category_id=categories['Desserts'].id,
            name='Mango Kulfi Falooda Royal',
            description='Rich authentic Alphonso mango kulfi served over silky vermicelli falooda noodles, sabja seeds, rose syrup, and roasted almonds.',
            ingredients='Alphonso Mango Pulp, Condensed Milk, Falooda Sev, Sabja Seeds, Rose Syrup, Almonds',
            price=159.00, food_type='veg', image='food/kulfi.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[6].id, category_id=categories['Beverages'].id,
            name='Iced Belgian Mocha Frappe',
            description='Chilled espresso blended with rich Belgian dark chocolate ganache, cold milk, and topped with whipped cream and cocoa dusting.',
            ingredients='Espresso Shot, Belgian Dark Chocolate, Whole Milk, Whipped Cream, Crushed Ice',
            price=179.00, food_type='veg', image='food/iced_coffee.svg', availability=True
        ),
        FoodItem(
            restaurant_id=rest_data[6].id, category_id=categories['Beverages'].id,
            name='Fresh Mint Lime Sparkling Soda',
            description='Refreshing chilled sparkling cooler infused with hand-crushed mint leaves, freshly squeezed key limes, and black rock salt.',
            ingredients='Sparkling Soda, Fresh Lime Juice, Mint Sprigs, Black Salt, Pure Cane Sugar',
            price=99.00, food_type='veg', image='food/lime_soda.svg', availability=True
        )
    ]
    db.session.add_all(foods)
    db.session.commit()

    # 5. Sample Orders
    order1 = Order(
        user_id=user1.id,
        total_amount=406.35,
        delivery_address='Flat 402, Green Valley Apartments, 12th Main Indiranagar, Bengaluru - 560038',
        phone='+91 9822012345',
        payment_method='Demo Online Payment',
        order_status='Delivered'
    )
    order2 = Order(
        user_id=user1.id,
        total_amount=606.90,
        delivery_address='Flat 402, Green Valley Apartments, 12th Main Indiranagar, Bengaluru - 560038',
        phone='+91 9822012345',
        payment_method='Cash on Delivery',
        order_status='Preparing'
    )
    order3 = Order(
        user_id=user2.id,
        total_amount=375.90,
        delivery_address='Bungalow 7, Lotus Enclave, Near Kothrud Stand, Pune - 411038',
        phone='+91 9876598765',
        payment_method='Demo Online Payment',
        order_status='Out for Delivery'
    )
    db.session.add_all([order1, order2, order3])
    db.session.commit()

    # 6. Sample Order Items
    item1 = OrderItem(order_id=order1.id, food_id=foods[0].id, quantity=1, price=349.00)
    item2 = OrderItem(order_id=order1.id, food_id=foods[10].id, quantity=1, price=55.00)
    item3 = OrderItem(order_id=order2.id, food_id=foods[3].id, quantity=1, price=389.00)
    item4 = OrderItem(order_id=order2.id, food_id=foods[5].id, quantity=1, price=149.00)
    item5 = OrderItem(order_id=order2.id, food_id=foods[19].id, quantity=1, price=99.00)
    item6 = OrderItem(order_id=order3.id, food_id=foods[6].id, quantity=1, price=229.00)
    item7 = OrderItem(order_id=order3.id, food_id=foods[8].id, quantity=1, price=129.00)
    db.session.add_all([item1, item2, item3, item4, item5, item6, item7])

    # 7. Sample Contact Messages
    msg1 = ContactMessage(
        name='Aman Verma',
        email='aman.verma@example.com',
        phone='+91 9988776655',
        message='I loved the speed of delivery and the packaging of Royal Biryani House! Excellent service.'
    )
    msg2 = ContactMessage(
        name='Sneha Mukherjee',
        email='sneha.m@example.com',
        phone='+91 9123456780',
        message='Do you plan to expand restaurant delivery to Electronic City Phase 1 soon?'
    )
    db.session.add_all([msg1, msg2])
    db.session.commit()


if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    print("[*] Running standalone database initialization...")
    success = init_database(app)
    if not success:
        sys.exit(1)
