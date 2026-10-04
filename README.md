# FoodExpress - Online Food Delivery System
> A full-stack, responsive, modern food delivery web application built with Python 3, Flask, MySQL 8.0, and Vanilla CSS3/Bootstrap 5. Ideal for a college mini project, semester submission, or learning project.

---

## 📌 Project Overview

**FoodExpress** is a complete, feature-rich online food ordering and express delivery system inspired by the workflows of platforms like Zomato and Swiggy, with an original brand identity, architecture, and UI.

### 🌟 Key Features
- **Customer Features:**
  - Secure User Registration & Login with Werkzeug password hashing.
  - Browse food categories: Biryani, Pizza, Burger, South Indian, North Indian, Chinese, Desserts, Beverages.
  - Restaurant Discovery: View cuisine, delivery times, locations, ratings, and delivery fees.
  - Live Food Search & Filters: Search by dish name, filter by category, price range, restaurant, or pure veg / non-veg.
  - Food Details Page: High-resolution images, full descriptions, key ingredients, rating badge, and quantity selector.
  - Shopping Cart: Add to cart, live quantity updates, remove items, clear cart, automated subtotal, delivery fee, 5% GST tax calculation, and free delivery thresholds (free above ₹499).
  - Checkout & Demo Payment: Customer delivery details, delivery instructions, Cash on Delivery (COD) or simulated Demo Online Payment (Credit/Debit Card, UPI).
  - Order Tracking Timeline: Interactive stepper showing status progression (`Order Placed` ➔ `Accepted` ➔ `Preparing` ➔ `Out for Delivery` ➔ `Delivered`).
  - Order History: Review past orders, payment modes, timestamped receipts, and itemized summaries.
  - User Profile: Update name, phone, address, and secure password changes.
  - Contact Us: Public feedback and inquiry form stored in the database.

- **Administrator Features:**
  - Dedicated Admin Portal (`/admin/login`).
  - Operations Dashboard: Real-time stat cards (Total Users, Total Restaurants, Total Food Items, Total Orders, Pending Orders, Delivered Orders, and Total Revenue).
  - Restaurant Management: Add, edit, delete, and view restaurants.
  - Food Item Management: Add, edit, delete, and toggle item availability (`Available` vs `Sold Out`).
  - Order Fulfillment Management: View all orders with status filter; change status with instant customer synchronization.
  - User Directory: Search customers and toggle account activation status (`Active` vs `Inactive`).
  - Feedback Center: View and manage customer inquiries.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla ES6+), Bootstrap 5.3, Bootstrap Icons, Google Fonts (Plus Jakarta Sans) |
| **Backend** | Python 3.10+, Flask 3.1, Flask-SQLAlchemy 3.1, Werkzeug (Password Hashing), python-dotenv |
| **Database** | MySQL 8.0+ (via PyMySQL connector & Cryptography) |
| **Architecture** | MVC / Modular Flask Routes, Session Authentication, Parameterized SQL Queries |

---

## 🗄️ Database Design (`online_food_delivery`)

The project uses 8 relational tables with proper Primary Keys, Foreign Keys, cascading rules, and indexes:
1. `users`: Customer & administrator accounts with hashed passwords.
2. `restaurants`: Partner restaurants and cloud kitchens.
3. `categories`: Cuisine categories (Biryani, Pizza, Burger, South Indian, etc.).
4. `food_items`: Menu catalog linked to restaurants and categories.
5. `cart`: User-specific shopping cart persistence.
6. `orders`: Order header records, payment details, addresses, and statuses.
7. `order_items`: Snapshot of items and prices at the time of placing an order.
8. `contact_messages`: Inquiries and customer feedback.

---

## 🚀 Setup & Installation Instructions

Follow these step-by-step instructions to run the application on your computer.

### Step 1: Prerequisites
Make sure you have installed:
1. **Python 3.10 or higher**: [Download Python](https://www.python.org/downloads/) (Check "Add Python to PATH" during installation)
2. **MySQL Server 8.0+** (or XAMPP / WampServer / MySQL Workbench): [Download MySQL](https://dev.mysql.com/downloads/installer/)

---

### Step 2: Database Setup in MySQL

1. Start your **MySQL Server** (using MySQL Command Line, MySQL Workbench, or XAMPP Control Panel).
2. Open your MySQL client / terminal:
   ```bash
   mysql -u root -p
   ```
3. Import the provided `database.sql` script:
   - **Method A (Command line):**
     ```bash
     mysql -u root -p < database.sql
     ```
   - **Method B (MySQL Workbench / phpMyAdmin):**
     Open `database.sql`, paste the contents into the query editor, and click **Execute**.
   - This script creates the `online_food_delivery` database, creates all 8 tables, and seeds realistic sample restaurants, food items, categories, demo users, orders, and messages.

---

### Step 3: Configure Environment Variables (`.env`)

1. In the project root directory, copy `.env.example` to `.env`:
   - On Windows (PowerShell):
     ```powershell
     Copy-Item .env.example .env
     ```
   - On Linux / macOS:
     ```bash
     cp .env.example .env
     ```
2. Open `.env` in a text editor (e.g. VS Code, Notepad) and enter your MySQL root password:
   ```ini
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_actual_mysql_password
   DB_NAME=online_food_delivery
   SECRET_KEY=foodexpress_college_project_key_2026

   # Note: Leave USE_SQLITE=False to connect to MySQL
   USE_SQLITE=False
   ```

> 💡 **Quick Demo Tip:** If you do not have MySQL installed on your evaluation machine or want to quickly test the application without database setup, simply set `USE_SQLITE=True` in `.env`. The application will automatically initialize a local SQLite database with all tables and sample data!

---

### Step 4: Python Virtual Environment & Dependencies

1. Open your terminal in the `FoodExpress_Project` folder:
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - **Windows (Command Prompt):**
     ```cmd
     venv\Scripts\activate
     ```
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux:**
     ```bash
     source venv/bin/activate
     ```
4. Install all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

### Step 5: Run the Flask Application

Start the web server:
```bash
python app.py
```

You should see output similar to:
```text
[*] Starting FoodExpress Online Food Delivery System...
[*] Verified MySQL database 'online_food_delivery'.
[*] Database tables created/verified successfully.
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

### Step 6: Giving Access to Everyone (Publishing to Public Internet / Local Network)

To allow other people (friends, evaluation panels, mobile devices) to access FoodExpress:

#### Option A: 1-Click Server + Public Tunnel Launcher (Recommended)
Double-click `start_foodexpress.bat` (or `start_public.bat`):
- Launches the Flask server in its own console.
- Launches the Cloudflare Tunnel and prints a public HTTPS link:
  👉 `https://xxxxxxxx.trycloudflare.com`
- Anyone in the world can open this link on their smartphone, tablet, or PC to use FoodExpress!

#### Option B: Same Wi-Fi / Local Network Access
Since the server binds to `0.0.0.0`, any device on the same local network or Wi-Fi can directly open:
👉 `http://<your-local-ip>:5000` (e.g. `http://10.95.96.160:5000`)

---

## 🔑 Demo Login Accounts

| Role | Email Address | Password | Permissions |
|---|---|---|---|
| **Super Admin** | `admin@foodexpress.com` | `Admin@123` | Full access to Admin Dashboard, Restaurant & Food CRUD, Order status dispatch, User management, Feedback |
| **Demo Customer 1** | `rahul@example.com` | `User@123` | Ordering, Cart management, Profile, Tracking, Order history |
| **Demo Customer 2** | `priya@example.com` | `User@123` | Ordering, Cart management, Profile, Tracking, Order history |

---

## 🧪 Testing the Complete Workflow

1. **Browse Food:**
   - On the homepage, browse popular categories (Biryani, Pizza, Burger, Dosa).
   - Click "Explore Menu" or use the top search bar.
   - Filter by "Pure Vegetarian", price range, or category.
2. **Add to Cart:**
   - Click "Add to Cart" on any dish. Watch the navbar cart badge update in real-time.
   - Open `/cart` to adjust quantities or see the automated tax and free delivery calculations.
3. **Place Order:**
   - Click "Proceed to Checkout".
   - Confirm delivery address and contact phone.
   - Choose "Cash on Delivery" or "Demo Online Payment".
   - If "Demo Online Payment" is chosen, an academic card payment modal opens. Click "Authorize & Pay".
   - You will see the confirmation screen with a unique Order ID (`ORD#XXXX`).
4. **Track Order:**
   - Click "Track Order Status". Watch the animated status progression stepper.
5. **Admin Order Fulfillment:**
   - Sign out, or open an Incognito window and visit `http://127.0.0.1:5000/admin/login`.
   - Log in with `admin@foodexpress.com` / `Admin@123`.
   - On the Dashboard, observe the live metrics cards.
   - Go to "Orders Management" (`/admin/orders`). Locate your new order.
   - Change the order status from `Order Placed` ➔ `Accepted` ➔ `Preparing` ➔ `Out for Delivery` ➔ `Delivered`.
   - Refresh the customer tracking page in your other window: the status and stepper update immediately!

---

## 📁 Project Directory Structure

```text
FoodExpress_Project/
│
├── app.py                  # Main Flask application and REST routes
├── config.py               # Environment configuration and DB engine settings
├── models.py               # SQLAlchemy database models (8 tables)
├── init_db.py              # Auto database verification & data seeder
├── test_app.py             # Automated test suite (all customer & admin flows)
├── requirements.txt        # Python package dependencies
├── database.sql            # Full MySQL schema DDL & sample INSERT data
├── .env.example            # Environment variables template
├── README.md               # Complete setup and user documentation
│
├── templates/              # Jinja2 HTML5 Templates
│   ├── base.html           # Master layout with responsive navbar and footer
│   ├── index.html          # Homepage with hero, categories, and restaurants
│   ├── login.html          # User login
│   ├── register.html       # User registration
│   ├── profile.html        # Profile management & password change
│   ├── restaurants.html    # Restaurant directory
│   ├── restaurant_menu.html# Restaurant menu view
│   ├── menu.html           # Full food catalog with multi-filters
│   ├── food_details.html   # Detailed dish view with ingredients & qty
│   ├── cart.html           # Interactive shopping cart
│   ├── checkout.html       # Checkout & demo payment modal
│   ├── order_success.html  # Order confirmation with unique ID
│   ├── orders.html         # User past order history
│   ├── order_details.html  # Live order tracking stepper
│   ├── about.html          # About FoodExpress & 3-step guide
│   ├── contact.html        # Contact inquiry form
│   │
│   └── admin/              # Administrator Portal Templates
│       ├── base_admin.html     # Admin layout with sidebar
│       ├── login.html          # Secure admin login
│       ├── dashboard.html      # 7 Metric cards & quick actions
│       ├── restaurants.html    # Restaurant partner listing
│       ├── restaurant_form.html# Add / Edit restaurant
│       ├── food_items.html     # Food dish inventory & availability toggle
│       ├── food_form.html      # Add / Edit food dish
│       ├── orders.html         # Live order fulfillment table
│       ├── order_details.html  # Order inspection & status dispatcher
│       ├── users.html          # Registered user accounts & activation toggle
│       └── messages.html       # Customer feedback inquiries
│
├── static/                 # Static Assets
│   ├── css/
│   │   ├── style.css       # Core design system, variables, tokens & components
│   │   └── admin.css       # Admin dashboard, sidebar & table styles
│   │
│   ├── js/
│   │   ├── main.js         # Toast alerts & global interactive UI helpers
│   │   ├── cart.js         # AJAX Add to Cart, quantity adjustment, clear cart
│   │   ├── checkout.js     # Form validation & demo payment simulation
│   │   └── admin.js        # Admin sidebar toggle & table search
│   │
│   └── images/             # Vector SVGs (100% offline-ready)
│       ├── hero_food.svg   # Hero banner graphic
│       ├── categories/     # Category icons (biryani, pizza, burger, etc.)
│       ├── restaurants/    # Restaurant brand banners
│       └── food/           # Food dishes (chicken biryani, pizza, noodles, etc.)
│
└── utils/
    ├── __init__.py
    └── helpers.py          # Auth decorators, cart math, tracking calculations
```

---

## ❓ Common Errors & Solutions

1. **`Access denied for user 'root'@'localhost'`**:
   - Check your password in `.env`. Ensure `DB_PASSWORD` matches your local MySQL root password.
2. **`Can't connect to MySQL server on 'localhost'`**:
   - Verify that your MySQL service is running in Windows Services or XAMPP Control Panel.
   - Alternatively, set `USE_SQLITE=True` in `.env` to run the project using SQLite without needing MySQL.
3. **`ModuleNotFoundError: No module named 'flask'`**:
   - Ensure your virtual environment is activated (`venv\Scripts\activate`) before running `pip install -r requirements.txt`.
4. **`Port 5000 is in use`**:
   - Change the port in `app.py`: change `app.run(port=5000)` to `app.run(port=5001)`.

---

## 📄 License & Credits
Developed as an academic mini project demonstrating full-stack web development with Flask and MySQL. Free to use for learning, project viva, and portfolio demonstrations.
