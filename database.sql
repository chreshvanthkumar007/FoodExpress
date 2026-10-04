-- =======================================================
-- Online Food Delivery System - Database Schema & Sample Data
-- Database: online_food_delivery
-- Suitable for MySQL 8.0+
-- =======================================================

-- Create Database if not exists
CREATE DATABASE IF NOT EXISTS `online_food_delivery` 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `online_food_delivery`;

-- -------------------------------------------------------
-- 1. Table structure for table `users`
-- -------------------------------------------------------
DROP TABLE IF EXISTS `order_items`;
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `cart`;
DROP TABLE IF EXISTS `food_items`;
DROP TABLE IF EXISTS `categories`;
DROP TABLE IF EXISTS `restaurants`;
DROP TABLE IF EXISTS `contact_messages`;
DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(100) NOT NULL UNIQUE,
  `phone` VARCHAR(20) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `address` TEXT NOT NULL,
  `role` VARCHAR(20) NOT NULL DEFAULT 'user',
  `status` VARCHAR(20) NOT NULL DEFAULT 'active',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------
-- 2. Table structure for table `restaurants`
-- -------------------------------------------------------
CREATE TABLE `restaurants` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT DEFAULT NULL,
  `cuisine` VARCHAR(100) NOT NULL,
  `location` VARCHAR(150) NOT NULL,
  `delivery_time` VARCHAR(50) NOT NULL DEFAULT '30-40 mins',
  `delivery_fee` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `rating` DECIMAL(2,1) NOT NULL DEFAULT 4.5,
  `image` VARCHAR(255) DEFAULT NULL,
  `status` VARCHAR(20) NOT NULL DEFAULT 'active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------
-- 3. Table structure for table `categories`
-- -------------------------------------------------------
CREATE TABLE `categories` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL UNIQUE,
  `image` VARCHAR(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------
-- 4. Table structure for table `food_items`
-- -------------------------------------------------------
CREATE TABLE `food_items` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `restaurant_id` INT NOT NULL,
  `category_id` INT NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT DEFAULT NULL,
  `ingredients` TEXT DEFAULT NULL,
  `price` DECIMAL(10,2) NOT NULL,
  `food_type` VARCHAR(20) NOT NULL DEFAULT 'veg',
  `image` VARCHAR(255) DEFAULT NULL,
  `availability` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX (`name`),
  CONSTRAINT `fk_food_restaurant` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurants` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_food_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------
-- 5. Table structure for table `cart`
-- -------------------------------------------------------
CREATE TABLE `cart` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `food_id` INT NOT NULL,
  `quantity` INT NOT NULL DEFAULT 1,
  UNIQUE KEY `uq_user_food_cart` (`user_id`, `food_id`),
  CONSTRAINT `fk_cart_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_cart_food` FOREIGN KEY (`food_id`) REFERENCES `food_items` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------
-- 6. Table structure for table `orders`
-- -------------------------------------------------------
CREATE TABLE `orders` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `total_amount` DECIMAL(10,2) NOT NULL,
  `delivery_address` TEXT NOT NULL,
  `phone` VARCHAR(20) NOT NULL,
  `payment_method` VARCHAR(50) NOT NULL DEFAULT 'Cash on Delivery',
  `order_status` VARCHAR(50) NOT NULL DEFAULT 'Order Placed',
  `order_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_orders_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------
-- 7. Table structure for table `order_items`
-- -------------------------------------------------------
CREATE TABLE `order_items` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `order_id` INT NOT NULL,
  `food_id` INT NOT NULL,
  `quantity` INT NOT NULL,
  `price` DECIMAL(10,2) NOT NULL,
  CONSTRAINT `fk_order_items_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_order_items_food` FOREIGN KEY (`food_id`) REFERENCES `food_items` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------
-- 8. Table structure for table `contact_messages`
-- -------------------------------------------------------
CREATE TABLE `contact_messages` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `phone` VARCHAR(20) DEFAULT NULL,
  `message` TEXT NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =======================================================
-- Sample Data Insertion
-- =======================================================

-- 1. Users (Admin password: Admin@123, User password: User@123)
INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password`, `address`, `role`, `status`, `created_at`) VALUES
(1, 'Administrator', 'admin@foodexpress.com', '+91 9876543210', 'scrypt:32768:8:1$NTg17Mb9hVp7hw59$d974b8073986287efdf16110b07fa084b70ea1c1aa74bd10f6ee8dc6c2003cb6c33a89ac1de60f81823258d7d7cfe6d3b9b322b193526fece8c1150e829f9670', 'FoodExpress Corporate Tower, MG Road, Bengaluru', 'admin', 'active', NOW()),
(2, 'Rahul Sharma', 'rahul@example.com', '+91 9822012345', 'scrypt:32768:8:1$lnVMe6W8w7eEHHbH$f78ace9daa39208d7303dcc0a25113aa98182be0bfb5fcb8abd8c793b5608e1f5d389bd1e8404e6f231f4e796154a6420027f76cff86789d2821481b605584a4', 'Flat 402, Green Valley Apartments, 12th Main Indiranagar, Bengaluru - 560038', 'user', 'active', NOW()),
(3, 'Priya Patel', 'priya@example.com', '+91 9876598765', 'scrypt:32768:8:1$lnVMe6W8w7eEHHbH$f78ace9daa39208d7303dcc0a25113aa98182be0bfb5fcb8abd8c793b5608e1f5d389bd1e8404e6f231f4e796154a6420027f76cff86789d2821481b605584a4', 'Bungalow 7, Lotus Enclave, Near Kothrud Stand, Pune - 411038', 'user', 'active', NOW());

-- 2. Categories
INSERT INTO `categories` (`id`, `name`, `image`) VALUES
(1, 'Biryani', 'categories/biryani.svg'),
(2, 'Pizza', 'categories/pizza.svg'),
(3, 'Burger', 'categories/burger.svg'),
(4, 'South Indian', 'categories/south_indian.svg'),
(5, 'North Indian', 'categories/north_indian.svg'),
(6, 'Chinese', 'categories/chinese.svg'),
(7, 'Desserts', 'categories/desserts.svg'),
(8, 'Beverages', 'categories/beverages.svg');

-- 3. Restaurants
INSERT INTO `restaurants` (`id`, `name`, `description`, `cuisine`, `location`, `delivery_time`, `delivery_fee`, `rating`, `image`, `status`) VALUES
(1, 'Royal Biryani House', 'Authentic slow-cooked Dum Biryanis, aromatic kebabs, and royal Mughlai gravies prepared with age-old secret spices.', 'Biryani, Mughlai, Kebabs', '100 Feet Rd, Indiranagar, Bengaluru', '25-35 mins', 40.00, 4.8, 'restaurants/royal_biryani.svg', 'active'),
(2, 'Pizza Paradiso', 'Handcrafted stone-oven Italian artisanal pizzas made with fresh mozzarella, sourdough crust, and imported herbs.', 'Italian, Pizza, Fast Food', '5th Block, Koramangala, Bengaluru', '30-40 mins', 35.00, 4.6, 'restaurants/pizza_paradiso.svg', 'active'),
(3, 'Burger Junction', 'Juicy grilled gourmet burgers, loaded seasoned peri-peri fries, and thick American style handcrafted milkshakes.', 'Burgers, American, Fast Food', 'Brigade Road, MG Road, Bengaluru', '20-30 mins', 30.00, 4.5, 'restaurants/burger_junction.svg', 'active'),
(4, 'Spice Symphony', 'Rich North Indian curries, melting butter paneer, tender tandoori dishes, and freshly baked clay-oven breads.', 'North Indian, Mughlai, Tandoor', 'Sector 2, HSR Layout, Bengaluru', '35-45 mins', 45.00, 4.7, 'restaurants/spice_symphony.svg', 'active'),
(5, 'Dakshin Flavors', 'Traditional South Indian crispy ghee dosas, fluffy steamed idlis, spicy vadas, and authentic filter coffee.', 'South Indian, Chettinad, Dosa', '4th Block, Jayanagar, Bengaluru', '20-25 mins', 25.00, 4.6, 'restaurants/dakshin_flavors.svg', 'active'),
(6, 'Dragon Wok', 'Sizzling Asian delicacies, Schezwan fried rice, spicy hakka noodles, steamed dim sums, and wok-tossed bowls.', 'Chinese, Asian, Pan-Asian', 'ITPL Main Rd, Whitefield, Bengaluru', '30-40 mins', 40.00, 4.4, 'restaurants/dragon_wok.svg', 'active'),
(7, 'Sweet Tooth Cafe', 'Heavenly handcrafted desserts, traditional warm Indian sweets with rabri, artisanal ice creams, and refreshing coolers.', 'Desserts, Bakery, Beverages', 'Church Street, Central Bengaluru', '15-25 mins', 30.00, 4.9, 'restaurants/sweet_tooth.svg', 'active');

-- 4. Food Items
INSERT INTO `food_items` (`id`, `restaurant_id`, `category_id`, `name`, `description`, `ingredients`, `price`, `food_type`, `image`, `availability`) VALUES
(1, 1, 1, 'Hyderabadi Chicken Dum Biryani', 'Aromatic long-grain basmati rice layered with succulent spiced chicken cuts, slow-cooked in handi seal with saffron & ghee.', 'Basmati Rice, Marinated Chicken, Saffron, Ghee, Mint, Fried Onions, Spices', 349.00, 'non-veg', 'food/chicken_biryani.svg', 1),
(2, 1, 1, 'Royal Veg Dum Biryani', 'Fragrant basmati rice cooked on dum with seasonal garden vegetables, paneer cubes, cashews, and aromatic spices.', 'Basmati Rice, Paneer, Carrots, Green Peas, Cashews, Saffron, Spices', 269.00, 'veg', 'food/veg_biryani.svg', 1),
(3, 1, 5, 'Mutton Galouti Kebab', 'Melt-in-mouth tender minced lamb kebabs marinated with raw papaya and 32 Awadhi secret spices, shallow fried in desi ghee.', 'Minced Mutton, Raw Papaya, Awadhi Spices, Desi Ghee, Kewra Essence', 399.00, 'non-veg', 'food/kebab.svg', 1),
(4, 2, 2, 'Farmhouse Supreme Pizza', 'Classic 10-inch hand-stretched crust topped with rich herb marinara, golden corn, bell peppers, button mushrooms, and melted mozzarella.', 'Pizza Dough, Tomato Marinara, Mozzarella, Bell Peppers, Mushrooms, Sweet Corn, Olives', 389.00, 'veg', 'food/veg_pizza.svg', 1),
(5, 2, 2, 'Peri Peri Chicken Feast Pizza', 'Spicy grilled peri-peri chicken chunks, roasted paprika, jalapenos, and smoked gouda on a thin crispy crust.', 'Pizza Dough, Marinara, Peri Peri Chicken, Smoked Gouda, Jalapenos, Red Paprika', 449.00, 'non-veg', 'food/chicken_pizza.svg', 1),
(6, 2, 2, 'Cheesy Garlic Breadsticks', 'Freshly baked buttery breadsticks infused with roasted garlic, herbs, and loaded with stretchy mozzarella cheese.', 'Bread Dough, Roasted Garlic Butter, Herbs, Mozzarella, Oregano Dip', 149.00, 'veg', 'food/garlic_bread.svg', 1),
(7, 3, 3, 'Crispy Double Decker Chicken Burger', 'Crispy spiced chicken fillet topped with melted cheddar, fresh iceberg lettuce, sliced tomatoes, and creamy signature burger mayo.', 'Sesame Brioche Bun, Fried Chicken Fillet, Cheddar Cheese, Pickles, Signature Sauce', 229.00, 'non-veg', 'food/chicken_burger.svg', 1),
(8, 3, 3, 'Classic Veg Crunchy Cheese Burger', 'Golden crispy vegetable patty stuffed with cheese, lettuce, pickled gherkins, and tangy Thousand Island dressing in a toasted brioche.', 'Brioche Bun, Crispy Veg Patty, Sliced Cheddar, Iceberg Lettuce, Thousand Island Sauce', 169.00, 'veg', 'food/veg_burger.svg', 1),
(9, 3, 3, 'Loaded Peri Peri Fries', 'Crispy golden potato fries generously tossed in spicy African bird eye peri-peri seasoning and drizzled with warm cheese sauce.', 'Potatoes, Peri Peri Seasoning, Warm Cheddar Drizzle, Fresh Herbs', 129.00, 'veg', 'food/fries.svg', 1),
(10, 4, 5, 'Paneer Butter Masala', 'Fresh cottage cheese cubes gently simmered in a velvety, rich tomato-cashew gravy finished with butter, cream, and kasuri methi.', 'Cottage Cheese (Paneer), Tomatoes, Cashew Paste, Butter, Heavy Cream, Kasuri Methi', 289.00, 'veg', 'food/paneer_butter_masala.svg', 1),
(11, 4, 5, 'Butter Garlic Naan', 'Soft and bubbly traditional clay-tandoor flatbread brushed with crushed garlic and abundant salted melted butter.', 'Refined Flour, Crushed Garlic, Salted Butter, Fresh Coriander, Nigella Seeds', 55.00, 'veg', 'food/butter_naan.svg', 1),
(12, 4, 5, 'Murgh Makhani Butter Chicken', 'Tender boneless chicken tikka cooked in an iconic smooth makhani tomato butter gravy with aromatic garam masala.', 'Chicken Tikka, Tomatoes, Butter, Fresh Cream, Ginger-Garlic, Fenugreek', 369.00, 'non-veg', 'food/butter_chicken.svg', 1),
(13, 5, 4, 'Ghee Roast Masala Dosa', 'Ultra-crispy fermented rice-lentil crepe roasted in pure golden ghee, filled with spiced potato masala, served with 3 chutneys & sambar.', 'Fermented Rice Batter, Pure Ghee, Spiced Potato Filling, Coconut Chutney, Sambar', 139.00, 'veg', 'food/masala_dosa.svg', 1),
(14, 5, 4, 'Steamed Idli & Medu Vada Combo', 'Two pillow-soft steamed rice idlis and one crispy medu vada served piping hot with fresh coconut chutney and spicy lentil sambar.', 'Rice, Urad Dal, Curry Leaves, Mustard Seeds, Coconut, Tamarind Sambar', 119.00, 'veg', 'food/idli_vada.svg', 1),
(15, 6, 6, 'Schezwan Egg Fried Rice', 'Aromatic wok-tossed basmati rice with scrambled eggs, crunchy spring onions, shredded carrots, and fiery home-made Schezwan sauce.', 'Basmati Rice, Fresh Eggs, Schezwan Sauce, Spring Onions, Garlic, Soy Sauce', 219.00, 'non-veg', 'food/fried_rice.svg', 1),
(16, 6, 6, 'Veg Hakka Noodles', 'Classic street-style stir-fried thin noodles tossed with crunchy cabbage, julienned capsicum, bean sprouts, and dark soy sauce.', 'Noodles, Cabbage, Capsicum, Carrots, Spring Onions, Dark Soy, White Pepper', 189.00, 'veg', 'food/hakka_noodles.svg', 1),
(17, 7, 7, 'Warm Gulab Jamun with Rabri', 'Two traditional melt-in-mouth fried milk dough dumplings soaked in rose-cardamom sugar syrup, served with creamy thickened rabri.', 'Khoya, Rose Sugar Syrup, Green Cardamom, Thickened Rabri, Pistachios', 129.00, 'veg', 'food/gulab_jamun.svg', 1),
(18, 7, 7, 'Mango Kulfi Falooda Royal', 'Rich authentic Alphonso mango kulfi served over silky vermicelli falooda noodles, sabja seeds, rose syrup, and roasted almonds.', 'Alphonso Mango Pulp, Condensed Milk, Falooda Sev, Sabja Seeds, Rose Syrup, Almonds', 159.00, 'veg', 'food/kulfi.svg', 1),
(19, 7, 8, 'Iced Belgian Mocha Frappe', 'Chilled espresso blended with rich Belgian dark chocolate ganache, cold milk, and topped with whipped cream and cocoa dusting.', 'Espresso Shot, Belgian Dark Chocolate, Whole Milk, Whipped Cream, Crushed Ice', 179.00, 'veg', 'food/iced_coffee.svg', 1),
(20, 7, 8, 'Fresh Mint Lime Sparkling Soda', 'Refreshing chilled sparkling cooler infused with hand-crushed mint leaves, freshly squeezed key limes, and black rock salt.', 'Sparkling Soda, Fresh Lime Juice, Mint Sprigs, Black Salt, Pure Cane Sugar', 99.00, 'veg', 'food/lime_soda.svg', 1);

-- 5. Sample Orders
INSERT INTO `orders` (`id`, `user_id`, `total_amount`, `delivery_address`, `phone`, `payment_method`, `order_status`, `order_date`) VALUES
(1001, 2, 406.35, 'Flat 402, Green Valley Apartments, 12th Main Indiranagar, Bengaluru - 560038', '+91 9822012345', 'Demo Online Payment', 'Delivered', DATE_SUB(NOW(), INTERVAL 2 DAY)),
(1002, 2, 606.90, 'Flat 402, Green Valley Apartments, 12th Main Indiranagar, Bengaluru - 560038', '+91 9822012345', 'Cash on Delivery', 'Preparing', DATE_SUB(NOW(), INTERVAL 45 MINUTE)),
(1003, 3, 375.90, 'Bungalow 7, Lotus Enclave, Near Kothrud Stand, Pune - 411038', '+91 9876598765', 'Demo Online Payment', 'Out for Delivery', DATE_SUB(NOW(), INTERVAL 20 MINUTE));

-- 6. Sample Order Items
INSERT INTO `order_items` (`id`, `order_id`, `food_id`, `quantity`, `price`) VALUES
-- Order 1001 Items (Chicken Dum Biryani 349 + 5% tax + free delivery = 366.45)
(1, 1001, 1, 1, 349.00),
(2, 1001, 11, 1, 55.00),
-- Order 1002 Items (Farmhouse Pizza 389 + Cheesy Garlic Bread 149 = 538 + 5% tax + free delivery)
(3, 1002, 4, 1, 389.00),
(4, 1002, 6, 1, 149.00),
(5, 1002, 20, 1, 99.00),
-- Order 1003 Items (Chicken Burger 229 + Loaded Fries 129 = 358 + tax)
(6, 1003, 7, 1, 229.00),
(7, 1003, 9, 1, 129.00);

-- 7. Sample Contact Messages
INSERT INTO `contact_messages` (`id`, `name`, `email`, `phone`, `message`, `created_at`) VALUES
(1, 'Aman Verma', 'aman.verma@example.com', '+91 9988776655', 'I loved the speed of delivery and the packaging of Royal Biryani House! Excellent service.', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(2, 'Sneha Mukherjee', 'sneha.m@example.com', '+91 9123456780', 'Do you plan to expand restaurant delivery to Electronic City Phase 1 soon?', DATE_SUB(NOW(), INTERVAL 1 DAY));
