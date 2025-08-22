import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import json
import os
from datetime import datetime
import uuid

# Data faylini yuklash
def load_data():
    """data.json faylidan ma'lumotlarni yuklash"""
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Agar fayl yo'q bo'lsa, standart ma'lumotlarni yaratish
        default_data = {
            "categories": {},
            "orders": [],
            "users": [],
            "settings": {
                "admin_id": 5833966360,
                "bot_token": "7123336998:AAE_4fH9cYCppxzfVbCVj3FHs5vxx1kzoqo",
                "payment_card": "8600 1234 5678 9012",
                "payment_owner": "AUX SHOP",
                "payment_bank": "NBU"
            }
        }
        save_data(default_data)
        return default_data

def save_data(data):
    """Ma'lumotlarni data.json fayliga saqlash"""
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Ma'lumotlarni yuklash
data = load_data()

# Bot token va admin ID ni data.json dan olish
BOT_TOKEN = data['settings']['bot_token']
ADMIN_ID = data['settings']['admin_id']
bot = telebot.TeleBot(BOT_TOKEN)

# User data storage
user_data = {}
user_states = {}
contact_data = {}
admin_reply_data = {}

# Mahsulotlarni data.json dan olish
def get_products():
    """data.json dan mahsulotlarni olish (ichki kategoriyalar bilan)"""
    products = {}
    for category_key, category_data in data['categories'].items():
        if 'subcategories' in category_data:
            # Agar ichki kategoriyalar mavjud bo'lsa
            for subcategory_key, subcategory_data in category_data['subcategories'].items():
                full_key = f"{category_key}_{subcategory_key}"
                products[full_key] = subcategory_data['products']
        else:
            # Agar to'g'ridan-to'g'ri mahsulotlar bo'lsa
            products[category_key] = category_data.get('products', [])
    return products

# Ichki kategoriyalarni olish
def get_subcategories(category_key):
    """Berilgan kategoriya uchun ichki kategoriyalarni olish"""
    if category_key in data['categories']:
        category_data = data['categories'][category_key]
        if 'subcategories' in category_data:
            return category_data['subcategories']
    return {}

# Kategoriya ma'lumotlarini olish
def get_category_info(category_key, subcategory_key=None):
    """Kategoriya yoki ichki kategoriya ma'lumotlarini olish"""
    if category_key in data['categories']:
        category_data = data['categories'][category_key]
        if subcategory_key and 'subcategories' in category_data:
            if subcategory_key in category_data['subcategories']:
                return category_data['subcategories'][subcategory_key]
        else:
            return category_data
    return None

# Mahsulotlarni yangilash
def update_products():
    """data.json dan mahsulotlarni yangilash"""
    global products
    products = get_products()

# Dastlabki mahsulotlarni yuklash
products = get_products()

def create_main_menu(user_id=None):
    """Asosiy menyu yaratish"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Foydalanuvchi tilini olish
    user_lang = 'uz'  # Default til
    
    # Avval user_data dan olish
    if user_id and user_id in user_data:
        user_lang = user_data[user_id].get('language', 'uz')
    
    # Agar user_data da yo'q bo'lsa, data.json dan olish
    if user_lang == 'uz' and user_id:
        for user in data['users']:
            if user.get('id') == user_id:
                user_lang = user.get('language', 'uz')
                # user_data ga ham saqlash
                if user_id not in user_data:
                    user_data[user_id] = {'cart': [], 'language': user_lang, 'orders': []}
                else:
                    user_data[user_id]['language'] = user_lang
                break
    
    # Debug uchun print
    print(f"create_main_menu: User ID: {user_id}, Til: {user_lang}")
    print(f"user_data mavjud: {user_id in user_data}")
    if user_id in user_data:
        print(f"user_data[{user_id}]: {user_data[user_id]}")
    
    # Tilga qarab tugma matnlari
    button_texts = {
        'uz': {
            'categories': "🛍️ Kategoriyalar",
            'search': "🔍 Qidiruv",
            'cart': "🛒 Savat",
            'language': "🌐 Til",
            'orders': "📋 Buyurtmalar",
            'contact': "📞 Aloqa",
            'admin': "🔧 Admin Panel"
        },
        'ru': {
            'categories': "🛍️ Категории",
            'search': "🔍 Поиск",
            'cart': "🛒 Корзина",
            'language': "🌐 Язык",
            'orders': "📋 Заказы",
            'contact': "📞 Контакты",
            'admin': "🔧 Админ панель"
        },
        'en': {
            'categories': "🛍️ Categories",
            'search': "🔍 Search",
            'cart': "🛒 Cart",
            'language': "🌐 Language",
            'orders': "📋 Orders",
            'contact': "📞 Contact",
            'admin': "🔧 Admin Panel"
        }
    }
    
    texts = button_texts[user_lang]
    
    # Asosiy tugmalar (barcha foydalanuvchilar uchun)
    markup.add(
        KeyboardButton(texts['categories']),
        KeyboardButton(texts['search']),
        KeyboardButton(texts['cart']),
        KeyboardButton(texts['language']),
        KeyboardButton(texts['orders']),
        KeyboardButton(texts['contact'])
    )
    
    # Admin panel tugmasi faqat admin uchun
    if user_id == ADMIN_ID:
        markup.add(KeyboardButton(texts['admin']))
    return markup

def create_admin_main_menu():
    """Admin uchun asosiy menyu yaratish"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Admin uchun har doim o'zbek tilida (admin panel uchun)
    button_texts = {
        'categories': "🛍️ Kategoriyalar",
        'search': "🔍 Qidiruv",
        'cart': "🛒 Savat",
        'language': "🌐 Til",
        'orders': "📋 Buyurtmalar",
        'contact': "📞 Aloqa",
        'admin': "🔧 Admin Panel"
    }
    
    markup.add(
        KeyboardButton(button_texts['categories']),
        KeyboardButton(button_texts['search']),
        KeyboardButton(button_texts['cart']),
        KeyboardButton(button_texts['language']),
        KeyboardButton(button_texts['orders']),
        KeyboardButton(button_texts['contact']),
        KeyboardButton(button_texts['admin'])
    )
    return markup

def create_admin_menu():
    """Admin menyusini yaratish"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📊 Statistika"),
        KeyboardButton("📦 Mahsulotlar"),
        KeyboardButton("🏷️ Kategoriyalar"),
        KeyboardButton("📋 Buyurtmalar"),
        KeyboardButton("👥 Foydalanuvchilar"),
        KeyboardButton("⚙️ Sozlamalar"),
        KeyboardButton("🗑️ Hammasini o'chirish"),
        KeyboardButton("🔙 Asosiy menyu")
    )
    return markup

def create_category_menu():
    """Kategoriyalar menyusini yaratish"""
    markup = InlineKeyboardMarkup(row_width=1)
    
    # Mahsulotlarni yangilash
    update_products()
    
    for category_key, category_data in data['categories'].items():
        emoji = category_data.get('emoji', '📦')
        name = category_data['name']
        
        # Mahsulotlar sonini hisoblash
        if 'subcategories' in category_data:
            # Ichki kategoriyalar mavjud
            total_products = 0
            for subcategory_data in category_data['subcategories'].values():
                total_products += len(subcategory_data.get('products', []))
            product_count = total_products
        else:
            # To'g'ridan-to'g'ri mahsulotlar
            product_count = len(category_data.get('products', []))
        
        # Kategoriyalarni ko'rsatish
        markup.add(InlineKeyboardButton(
            f"{emoji} {name} ({product_count} ta)",
            callback_data=f"category_{category_key}"
        ))
    
    # Agar hech qanday kategoriya yo'q bo'lsa
    if not markup.keyboard:
        markup.add(InlineKeyboardButton("❌ Kategoriyalar yo'q", callback_data="no_categories"))
    
    return markup

def create_subcategory_menu(category_key):
    """Ichki kategoriyalar menyusini yaratish"""
    markup = InlineKeyboardMarkup(row_width=1)
    
    subcategories = get_subcategories(category_key)
    
    for subcategory_key, subcategory_data in subcategories.items():
        emoji = subcategory_data.get('emoji', '📦')
        name = subcategory_data['name']
        product_count = len(subcategory_data.get('products', []))
        
        markup.add(InlineKeyboardButton(
            f"{emoji} {name} ({product_count} ta)",
            callback_data=f"subcategory_{category_key}_{subcategory_key}"
        ))
    
    # Orqaga qaytish tugmasi
    markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_categories"))
    
    return markup

def create_language_menu():
    """Til tanlash menyusini yaratish"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")
    )
    return markup

def create_location_keyboard():
    """Lokatsiya yuborish uchun klaviatura"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        KeyboardButton("📍 Lokatsiyani yuborish", request_location=True),
        KeyboardButton("🔙 Bekor qilish")
    )
    return markup

# Admin komandalari
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    """Admin panel"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    admin_text = """
🔧 **Admin Panel**

Quyidagi funksiyalardan birini tanlang:
📊 Statistika - umumiy ma'lumotlar
📦 Mahsulotlar - mahsulotlarni boshqarish
🏷️ Kategoriyalar - kategoriyalarni boshqarish
📋 Buyurtmalar - buyurtmalarni ko'rish
👥 Foydalanuvchilar - foydalanuvchilar ro'yxati
⚙️ Sozlamalar - bot sozlamalari
    """
    
    bot.reply_to(message, admin_text, reply_markup=create_admin_menu())

@bot.message_handler(commands=['start'])
def start(message):
    """Botni boshlash"""
    user_id = message.from_user.id
    user_data[user_id] = {
        'cart': [],
        'language': 'uz',
        'orders': []
    }
    
    # Foydalanuvchini data.json ga qo'shish
    user_info = {
        'id': user_id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
        'joined_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'last_activity': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Agar foydalanuvchi mavjud bo'lmasa, qo'shish
    user_exists = False
    for user in data['users']:
        if user['id'] == user_id:
            user['last_activity'] = user_info['last_activity']
            user_exists = True
            break
    
    if not user_exists:
        data['users'].append(user_info)
        save_data(data)
    
    # Admin uchun maxsus xabar va menyu
    print(f"Start funksiyasi. User ID: {user_id}, Admin ID: {ADMIN_ID}")
    
    # Foydalanuvchi tilini olish
    user_lang = user_data[user_id].get('language', 'uz')
    
    # Tilga qarab xabar matnlari
    welcome_messages = {
        'uz': {
            'admin': """
🎉 Xush kelibsiz! Online do'kon botiga!

Quyidagi tugmalardan birini tanlang:
🛍️ Kategoriyalar - mahsulotlarni ko'rish
🔍 Qidiruv - mahsulotlarni qidirish
🛒 Savat - tanlangan mahsulotlar
🌐 Til - tilni o'zgartirish
📋 Buyurtmalar - buyurtmalar tarixi
📞 Aloqa - operator bilan bog'lanish
🔧 Admin Panel - bot boshqaruvi
            """,
            'user': """
🎉 Xush kelibsiz! Online do'kon botiga!

Quyidagi tugmalardan birini tanlang:
🛍️ Kategoriyalar - mahsulotlarni ko'rish
🔍 Qidiruv - mahsulotlarni qidirish
🛒 Savat - tanlangan mahsulotlar
🌐 Til - tilni o'zgartirish
📋 Buyurtmalar - buyurtmalar tarixi
📞 Aloqa - operator bilan bog'lanish
            """
        },
        'ru': {
            'admin': """
🎉 Добро пожаловать! В онлайн магазин бот!

Выберите одну из следующих кнопок:
🛍️ Категории - просмотр товаров
🔍 Поиск - поиск товаров
🛒 Корзина - выбранные товары
🌐 Язык - изменить язык
📋 Заказы - история заказов
📞 Контакты - связь с оператором
🔧 Админ панель - управление ботом
            """,
            'user': """
🎉 Добро пожаловать! В онлайн магазин бот!

Выберите одну из следующих кнопок:
🛍️ Категории - просмотр товаров
🔍 Поиск - поиск товаров
🛒 Корзина - выбранные товары
🌐 Язык - изменить язык
📋 Заказы - история заказов
📞 Контакты - связь с оператором
            """
        },
        'en': {
            'admin': """
🎉 Welcome! To the online store bot!

Choose one of the following buttons:
🛍️ Categories - view products
🔍 Search - search products
🛒 Cart - selected products
🌐 Language - change language
📋 Orders - order history
📞 Contact - contact operator
🔧 Admin Panel - bot management
            """,
            'user': """
🎉 Welcome! To the online store bot!

Choose one of the following buttons:
🛍️ Categories - view products
🔍 Search - search products
🛒 Cart - selected products
🌐 Language - change language
📋 Orders - order history
📞 Contact - contact operator
            """
        }
    }
    
    if user_id == ADMIN_ID:
        welcome_text = welcome_messages[user_lang]['admin']
        bot.reply_to(message, welcome_text, reply_markup=create_admin_main_menu())
    else:
        welcome_text = welcome_messages[user_lang]['user']
        bot.reply_to(message, welcome_text, reply_markup=create_main_menu(user_id))

@bot.message_handler(func=lambda message: message.text in ["🛍️ Kategoriyalar", "🛍️ Категории", "🛍️ Categories"])
def show_categories(message):
    """Kategoriyalarni ko'rsatish"""
    user_id = message.from_user.id
    user_lang = user_data.get(user_id, {}).get('language', 'uz')
    
    # Tilga qarab xabar matni
    messages = {
        'uz': "Mahsulot kategoriyalarini tanlang:",
        'ru': "Выберите категорию товаров:",
        'en': "Select product category:"
    }
    
    bot.reply_to(message, messages[user_lang], reply_markup=create_category_menu())

@bot.message_handler(func=lambda message: message.text in ["🔍 Qidiruv", "🔍 Поиск", "🔍 Search"])
def start_search(message):
    """Qidiruvni boshlash"""
    user_id = message.from_user.id
    user_states[user_id] = "searching"
    user_lang = user_data.get(user_id, {}).get('language', 'uz')
    
    # Tilga qarab xabar matnlari
    messages = {
        'uz': {
            'title': "🔍 Qanday mahsulot qidirayapsiz?",
            'description': "Mahsulot nomini yoki kalit so'zlarni yozing (masalan: iPhone, kurtka, kitob)",
            'back': "🔙 Asosiy menyu"
        },
        'ru': {
            'title': "🔍 Какой товар ищете?",
            'description': "Напишите название товара или ключевые слова (например: iPhone, куртка, книга)",
            'back': "🔙 Главное меню"
        },
        'en': {
            'title': "🔍 What product are you looking for?",
            'description': "Write the product name or keywords (for example: iPhone, jacket, book)",
            'back': "🔙 Main menu"
        }
    }
    
    msg = messages[user_lang]
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton(msg['back']))
    
    bot.reply_to(message, 
                 f"{msg['title']}\n\n{msg['description']}",
                 reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "searching" and message.text != "🔙 Asosiy menyu")
def handle_search(message):
    """Qidiruv natijalarini ko'rsatish"""
    user_id = message.from_user.id
    search_query = message.text.lower()
    
    # Barcha mahsulotlardan qidirish
    found_products = []
    
    for category, category_products in products.items():
        for product in category_products:
            if (search_query in product['name'].lower() or 
                search_query in product['description'].lower()):
                found_products.append((product, category))
    
    if not found_products:
        bot.reply_to(message, 
                     f"❌ '{message.text}' uchun mahsulot topilmadi.\n\n"
                     "Boshqa kalit so'zlar bilan qayta urinib ko'ring yoki kategoriyalarni ko'ring.")
        return
    
    # Natijalarni ko'rsatish
    result_text = f"🔍 '{message.text}' uchun topilgan mahsulotlar ({len(found_products)} ta):\n\n"
    
    markup = InlineKeyboardMarkup(row_width=1)
    
    for i, (product, category) in enumerate(found_products):
        # Category display names for search results
        category_names = {
            "telefonlar": "Telefonlar",
            "noutbuklar": "Noutbuklar", 
            "kiyimlar": "Kiyimlar",
            "konditsionerlar": "Konditsionerlar",
            "monitorlar": "Monitorlar",
            "klaviatura_va_mishkalar": "Klaviatura va Mishkalar",
            "kulerlar": "Kulerlar",
            "kir_yuvish_mashinalari": "Kir yuvish mashinalari"
        }
        
        display_name = category_names.get(category, category.capitalize())
        
        result_text += f"📦 {product['name']}\n"
        result_text += f"💰 {product['price']:,} so'm\n"
        result_text += f"📦 Mavjud: {product.get('quantity', 0)} ta\n"
        result_text += f"📝 {product['description']}\n"
        result_text += f"🏷️ Kategoriya: {display_name}\n\n"
        
        available_qty = product.get('quantity', 0)
        markup.add(InlineKeyboardButton(
            f"📦 {product['name']} - {product['price']:,} so'm ({available_qty} ta)",
            callback_data=f"search_product_{category}_{list(products[category]).index(product)}"
        ))
    
    markup.add(InlineKeyboardButton("🔙 Qayta qidirish", callback_data="search_again"))
    
    bot.reply_to(message, result_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🔙 Asosiy menyu")
def back_to_main_menu(message):
    """Asosiy menyuga qaytish"""
    user_id = message.from_user.id
    if user_id in user_states:
        del user_states[user_id]
    if user_id in contact_data:
        del contact_data[user_id]
    
    # Admin uchun maxsus menyu
    if user_id == ADMIN_ID:
        bot.reply_to(message, "🏠 Asosiy menyuga qaytdingiz!", reply_markup=create_admin_main_menu())
    else:
        bot.reply_to(message, "🏠 Asosiy menyuga qaytdingiz!", reply_markup=create_main_menu(user_id))

@bot.message_handler(func=lambda message: message.text in ["🛒 Savat", "🛒 Корзина", "🛒 Cart"])
def show_cart(message):
    """Savatni ko'rsatish"""
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {'cart': [], 'language': 'uz', 'orders': []}
    
    cart = user_data[user_id]['cart']
    user_lang = user_data[user_id].get('language', 'uz')
    
    # Tilga qarab xabar matnlari
    messages = {
        'uz': {
            'empty': "🛒 Savatingiz bo'sh!",
            'title': "🛒 Savatingizdagi mahsulotlar:\n\n",
            'quantity': "🔢 Miqdor: {} ta",
            'price': "💰 Narxi: {} so'm",
            'total': "💵 Jami: {} so'm",
            'description': "📝 {}",
            'total_sum': "💵 Jami: {} so'm",
            'order': "✅ Buyurtma berish",
            'clear': "🗑️ Savatni tozalash"
        },
        'ru': {
            'empty': "🛒 Ваша корзина пуста!",
            'title': "🛒 Товары в вашей корзине:\n\n",
            'quantity': "🔢 Количество: {} шт",
            'price': "💰 Цена: {} сум",
            'total': "💵 Итого: {} сум",
            'description': "📝 {}",
            'total_sum': "💵 Итого: {} сум",
            'order': "✅ Оформить заказ",
            'clear': "🗑️ Очистить корзину"
        },
        'en': {
            'empty': "🛒 Your cart is empty!",
            'title': "🛒 Products in your cart:\n\n",
            'quantity': "🔢 Quantity: {} pcs",
            'price': "💰 Price: {} sum",
            'total': "💵 Total: {} sum",
            'description': "📝 {}",
            'total_sum': "💵 Total: {} sum",
            'order': "✅ Place order",
            'clear': "🗑️ Clear cart"
        }
    }
    
    msg = messages[user_lang]
    
    if not cart:
        bot.reply_to(message, msg['empty'])
        return
    
    cart_text = msg['title']
    total = 0
    
    for item in cart:
        quantity = item.get('quantity', 1)
        price_per_item = item.get('unit_price', item['price'])
        total_price = item.get('total_price', price_per_item * quantity)
        
        cart_text += f"📦 {item['name']}\n"
        
        # Parametr ma'lumotini ko'rsatish
        if 'selected_param' in item:
            param = item['selected_param']
            param_price = param.get('price', 0)
            if param_price > 0:
                cart_text += f"⚙️ {param['name']}: {param['value']} (+{param_price:,} so'm)\n"
            else:
                cart_text += f"⚙️ {param['name']}: {param['value']}\n"
        
        cart_text += f"{msg['quantity'].format(quantity)}\n"
        cart_text += f"{msg['price'].format(price_per_item)}\n"
        cart_text += f"{msg['total'].format(total_price)}\n"
        cart_text += f"{msg['description'].format(item['description'])}\n\n"
        total += total_price
    
    cart_text += msg['total_sum'].format(total)
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(msg['order'], callback_data="checkout"))
    markup.add(InlineKeyboardButton(msg['clear'], callback_data="clear_cart"))
    
    bot.reply_to(message, cart_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🌐 Til")
def show_languages(message):
    """Til tanlash menyusini ko'rsatish"""
    bot.reply_to(message, "Tilni tanlang:", reply_markup=create_language_menu())

@bot.message_handler(func=lambda message: message.text == "📋 Buyurtmalar")
def show_orders(message):
    """Buyurtmalarni ko'rsatish"""
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {'cart': [], 'language': 'uz', 'orders': []}
    
    orders = user_data[user_id]['orders']
    
    if not orders:
        bot.reply_to(message, "📋 Hali buyurtmalaringiz yo'q!")
        return
    
    orders_text = "📋 Buyurtmalaringiz:\n\n"
    
    for i, order in enumerate(orders, 1):
        orders_text += f"📦 Buyurtma #{i}\n"
        orders_text += f"📅 Sana: {order['date']}\n"
        orders_text += f"💰 Jami: {order['total']:,} so'm\n"
        orders_text += f"📝 Mahsulotlar: {', '.join(order['items'])}\n\n"
    
    bot.reply_to(message, orders_text)

@bot.message_handler(func=lambda message: message.text == "🔧 Admin Panel")
def admin_panel_button(message):
    """Admin Panel tugmasini bosganda"""
    print(f"Admin panel tugmasi bosildi. User ID: {message.from_user.id}, Admin ID: {ADMIN_ID}")
    if message.from_user.id != ADMIN_ID:
        print(f"Admin emas! User ID: {message.from_user.id}, Admin ID: {ADMIN_ID}")
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    admin_text = """
🔧 **Admin Panel**

Quyidagi funksiyalardan birini tanlang:
📊 Statistika - umumiy ma'lumotlar
📦 Mahsulotlar - mahsulotlarni boshqarish
🏷️ Kategoriyalar - kategoriyalarni boshqarish
📋 Buyurtmalar - buyurtmalarni ko'rish
👥 Foydalanuvchilar - foydalanuvchilar ro'yxati
⚙️ Sozlamalar - bot sozlamalari
    """
    
    bot.reply_to(message, admin_text, reply_markup=create_admin_menu())



# Keyboard button handlerlar (Admin panel asosiy tugmalari)
@bot.message_handler(func=lambda message: message.text == "📊 Statistika")
def admin_stats_button(message):
    """Admin statistika tugmasini bosganda"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    total_users = len(data['users'])
    total_orders = len(data['orders'])
    total_products = sum(len(cat['products']) for cat in data['categories'].values())
    total_categories = len(data['categories'])
    
    # Bugungi buyurtmalar
    today = datetime.now().strftime("%Y-%m-%d")
    today_orders = [order for order in data['orders'] if order['date'].startswith(today)]
    
    stats_text = f"""
📊 **Bot Statistikasi**

👥 **Foydalanuvchilar:**
• Jami: {total_users} ta
• Bugun faol: {len(today_orders)} ta

📦 **Mahsulotlar:**
• Kategoriyalar: {total_categories} ta
• Mahsulotlar: {total_products} ta

📋 **Buyurtmalar:**
• Jami: {total_orders} ta
• Bugun: {len(today_orders)} ta

💰 **Bugungi tushum:**
• {sum(order.get('total', 0) for order in today_orders):,} so'm
    """
    
    bot.reply_to(message, stats_text, reply_markup=create_admin_menu())

@bot.message_handler(func=lambda message: message.text == "📦 Mahsulotlar")
def admin_products_button(message):
    """Admin mahsulotlar tugmasini bosganda"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    products_text = """
📦 **Mahsulotlar Boshqaruvi**

Quyidagi amallardan birini tanlang:
➕ Mahsulot qo'shish - yangi mahsulot qo'shish
✏️ Mahsulot tahrirlash - mavjud mahsulotni o'zgartirish
🗑️ Mahsulot o'chirish - mahsulotni o'chirish
📊 Mahsulot statistikasi - mahsulotlar haqida ma'lumot
    """
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("➕ Mahsulot qo'shish"),
        KeyboardButton("✏️ Mahsulot tahrirlash"),
        KeyboardButton("🗑️ Mahsulot o'chirish"),
        KeyboardButton("📊 Mahsulot statistikasi"),
        KeyboardButton("🔙 Orqaga")
    )
    
    bot.reply_to(message, products_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🏷️ Kategoriyalar")
def admin_categories_button(message):
    """Admin kategoriyalar tugmasini bosganda"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    # Ichki kategoriyalar sonini hisoblash
    total_subcategories = 0
    for category_data in data['categories'].values():
        if 'subcategories' in category_data:
            total_subcategories += len(category_data['subcategories'])
    
    categories_text = f"""
🏷️ **Kategoriyalar Boshqaruvi**

📂 Asosiy kategoriyalar: {len(data['categories'])} ta
📁 Ichki kategoriyalar: {total_subcategories} ta

Quyidagi amallardan birini tanlang:
➕ Kategoriya qo'shish - yangi kategoriya qo'shish
📁 Ichki kategoriya qo'shish - ichki kategoriya qo'shish
✏️ Kategoriya tahrirlash - mavjud kategoriyani o'zgartirish
🗑️ Kategoriya o'chirish - kategoriyani o'chirish
    """
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("➕ Kategoriya qo'shish"),
        KeyboardButton("📁 Ichki kategoriya qo'shish"),
        KeyboardButton("✏️ Kategoriya tahrirlash"),
        KeyboardButton("🗑️ Kategoriya o'chirish"),
        KeyboardButton("🔙 Orqaga")
    )
    
    bot.reply_to(message, categories_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "✏️ Kategoriya tahrirlash")
def admin_edit_category_button(message):
    """Kategoriya tahrirlash tugmasini bosganda"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    if not data['categories']:
        bot.reply_to(message, "🏷️ Hali kategoriyalar yo'q!", reply_markup=create_admin_menu())
        return
    
    # Kategoriyalar ro'yxatini ko'rsatish
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    for category_key, category_data in data['categories'].items():
        emoji = category_data.get('emoji', '📦')
        name = category_data['name']
        product_count = len(category_data['products'])
        markup.add(KeyboardButton(f"{emoji} {name} ({product_count} ta mahsulot)"))
    
    markup.add(KeyboardButton("🔙 Orqaga"))
    
    bot.reply_to(message, 
                 "✏️ **Kategoriya tahrirlash**\n\n"
                 "Qaysi kategoriyani tahrirlamoqchisiz?\n"
                 "Kategoriya nomini tanlang:",
                 reply_markup=markup)
    
    user_states[message.from_user.id] = "admin_edit_category_select"

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_edit_category_select")
def handle_admin_edit_category_select(message):
    """Tahrirlash uchun kategoriya tanlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Orqaga":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        
        bot.reply_to(message, "❌ Kategoriya tahrirlash bekor qilindi.", reply_markup=create_admin_menu())
        return
    
    # Kategoriya nomini topish
    category_key = None
    for key, category_data in data['categories'].items():
        if category_data['name'] in message.text:
            category_key = key
            break
    
    if not category_key:
        bot.reply_to(message, "❌ Kategoriya topilmadi! Iltimos, qayta tanlang.")
        return
    
    # Kategoriya ma'lumotlarini saqlash
    if message.from_user.id not in contact_data:
        contact_data[message.from_user.id] = {}
    contact_data[message.from_user.id]['edit_category_key'] = category_key
    
    selected_category = data['categories'][category_key]
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📝 Nomi"),
        KeyboardButton("😀 Emoji"),
        KeyboardButton("🔙 Orqaga")
    )
    
    bot.reply_to(message, 
                 f"✏️ **Kategoriya tahrirlash**\n\n"
                 f"📦 **Kategoriya:** {selected_category['name']}\n"
                 f"😀 **Emoji:** {selected_category.get('emoji', '📦')}\n"
                 f"📊 **Mahsulotlar:** {len(selected_category['products'])} ta\n\n"
                 f"Qaysi qismini o'zgartirmoqchisiz?",
                 reply_markup=markup)
    
    user_states[message.from_user.id] = "admin_edit_category_field"

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_edit_category_field")
def handle_admin_edit_category_field(message):
    """Kategoriya qaysi qismini tahrirlashni tanlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Orqaga":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'edit_category_key' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['edit_category_key']
        
        bot.reply_to(message, "❌ Kategoriya tahrirlash bekor qilindi.", reply_markup=create_admin_menu())
        return
    
    field = message.text.strip()
    
    if field == "📝 Nomi":
        user_states[message.from_user.id] = "admin_edit_category_name"
        bot.reply_to(message, "📝 Yangi kategoriya nomini yozing:")
    elif field == "😀 Emoji":
        user_states[message.from_user.id] = "admin_edit_category_emoji"
        bot.reply_to(message, "😀 Yangi emoji yozing (masalan: 🎯):")
    else:
        bot.reply_to(message, "❌ Noto'g'ri tanlov! Iltimos, qayta tanlang.")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_edit_category_name")
def handle_admin_edit_category_name(message):
    """Kategoriya nomini tahrirlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        category_key = contact_data[message.from_user.id]['edit_category_key']
        old_name = data['categories'][category_key]['name']
        
        # Kategoriya nomini yangilash
        data['categories'][category_key]['name'] = message.text.strip()
        
        # data.json ga saqlash
        save_data(data)
        update_products()
        
        success_text = f"""
✅ Kategoriya nomi muvaffaqiyatli o'zgartirildi!

📦 **Eski nom:** {old_name}
📦 **Yangi nom:** {message.text.strip()}
        """
        
        bot.reply_to(message, success_text, reply_markup=create_admin_menu())
        
        # Foydalanuvchi holatini tozalash
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'edit_category_key' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['edit_category_key']
            
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik yuz berdi: {e}", reply_markup=create_admin_menu())

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_edit_category_emoji")
def handle_admin_edit_category_emoji(message):
    """Kategoriya emojisini tahrirlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        category_key = contact_data[message.from_user.id]['edit_category_key']
        old_emoji = data['categories'][category_key].get('emoji', '📦')
        
        # Kategoriya emojisini yangilash
        data['categories'][category_key]['emoji'] = message.text.strip()
        
        # data.json ga saqlash
        save_data(data)
        update_products()
        
        success_text = f"""
✅ Kategoriya emojisi muvaffaqiyatli o'zgartirildi!

😀 **Eski emoji:** {old_emoji}
😀 **Yangi emoji:** {message.text.strip()}
        """
        
        bot.reply_to(message, success_text, reply_markup=create_admin_menu())
        
        # Foydalanuvchi holatini tozalash
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'edit_category_key' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['edit_category_key']
            
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik yuz berdi: {e}", reply_markup=create_admin_menu())

@bot.message_handler(func=lambda message: message.text == "📋 Buyurtmalar")
def admin_orders_button(message):
    """Admin buyurtmalar tugmasini bosganda"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    if not data['orders']:
        bot.reply_to(message, "📋 Hali buyurtmalar yo'q!", reply_markup=create_admin_menu())
        return
    
    # Oxirgi 5 ta buyurtmani ko'rsatish
    recent_orders = data['orders'][-5:]
    
    orders_text = f"""
📋 **Buyurtmalar Boshqaruvi**

Jami buyurtmalar: {len(data['orders'])} ta

**Oxirgi buyurtmalar:**
"""
    
    for i, order in enumerate(reversed(recent_orders), 1):
        # Mahsulotlar ro'yxatini yaratish
        items_text = ", ".join(order.get('items', []))
        if len(items_text) > 50:
            items_text = items_text[:50] + "..."
        
        orders_text += f"""
{i}. 📦 Buyurtma #{len(data['orders']) - len(recent_orders) + i}
   👤 {order.get('customer_name', 'Noma lum')}
   📱 {order.get('customer_phone', 'Noma lum')}
   📍 {order.get('customer_address', 'Noma lum')}
   💰 {order.get('total', 0):,} so'm
   💳 {order.get('payment_method', 'Noma lum')}
   📅 {order.get('date', 'Noma lum')}
   📦 Mahsulotlar: {items_text}
"""
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📋 Barcha buyurtmalar"),
        KeyboardButton("🗑️ Buyurtma o'chirish"),
        KeyboardButton("🔙 Orqaga")
    )
    
    bot.reply_to(message, orders_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "👥 Foydalanuvchilar")
def admin_users_button(message):
    """Admin foydalanuvchilar tugmasini bosganda"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    if not data['users']:
        bot.reply_to(message, "👥 Hali foydalanuvchilar yo'q!", reply_markup=create_admin_menu())
        return
    
    # Oxirgi 10 ta foydalanuvchini ko'rsatish
    recent_users = data['users'][-10:]
    
    users_text = f"""
👥 **Foydalanuvchilar Boshqaruvi**

📊 **Statistika:**
• Jami foydalanuvchilar: {len(data['users'])} ta
• Oxirgi 24 soatda: {len([u for u in data['users'] if 'joined_date' in u and '2024' in u.get('joined_date', '')])} ta

**Oxirgi ro'yxatdan o'tganlar:**
"""
    
    for i, user in enumerate(reversed(recent_users), 1):
        username = user.get('username', 'Noma lum')
        first_name = user.get('first_name', 'Noma lum')
        last_name = user.get('last_name', '')
        user_id = user.get('user_id', 'Noma lum')
        joined_date = user.get('joined_date', 'Noma lum')
        
        full_name = f"{first_name} {last_name}".strip() if last_name else first_name
        
        users_text += f"""
{i}. 👤 {full_name}
   🆔 ID: {user_id}
   📧 @{username}
   📅 {joined_date}
"""
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("👥 Barcha foydalanuvchilar"),
        KeyboardButton("📊 Foydalanuvchi statistikasi"),
        KeyboardButton("🗑️ Foydalanuvchi o'chirish"),
        KeyboardButton("📋 Foydalanuvchi qidirish"),
        KeyboardButton("🔙 Orqaga")
    )
    
    bot.reply_to(message, users_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "👥 Barcha foydalanuvchilar")
def admin_all_users_button(message):
    """Barcha foydalanuvchilarni ko'rsatish"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    if not data['users']:
        bot.reply_to(message, "👥 Hali foydalanuvchilar yo'q!", reply_markup=create_admin_menu())
        return
    
    # Barcha foydalanuvchilarni ko'rsatish (sahifalarga bo'lib)
    page = 0
    users_per_page = 15
    
    if message.from_user.id not in contact_data:
        contact_data[message.from_user.id] = {}
    
    contact_data[message.from_user.id]['users_page'] = page
    
    start_index = page * users_per_page
    end_index = start_index + users_per_page
    page_users = data['users'][start_index:end_index]
    
    total_pages = (len(data['users']) + users_per_page - 1) // users_per_page
    
    users_text = f"""
👥 **Barcha Foydalanuvchilar**

📊 **Jami:** {len(data['users'])} ta foydalanuvchi
📄 **Sahifa:** {page + 1}/{total_pages}

"""
    
    for i, user in enumerate(page_users, start_index + 1):
        username = user.get('username', 'Noma lum')
        first_name = user.get('first_name', 'Noma lum')
        last_name = user.get('last_name', '')
        user_id = user.get('user_id', 'Noma lum')
        joined_date = user.get('joined_date', 'Noma lum')
        
        full_name = f"{first_name} {last_name}".strip() if last_name else first_name
        
        users_text += f"""
{i}. 👤 {full_name}
   🆔 ID: {user_id}
   📧 @{username}
   📅 {joined_date}
"""
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    
    if total_pages > 1:
        if page > 0:
            markup.add(KeyboardButton("⬅️ Oldingi"))
        if page < total_pages - 1:
            markup.add(KeyboardButton("➡️ Keyingi"))
    
    markup.add(
        KeyboardButton("🔙 Orqaga"),
        KeyboardButton("📊 Foydalanuvchi statistikasi")
    )
    
    bot.reply_to(message, users_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["⬅️ Oldingi", "➡️ Keyingi"])
def admin_users_pagination(message):
    """Foydalanuvchilar sahifalarini boshqarish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.from_user.id not in contact_data or 'users_page' not in contact_data[message.from_user.id]:
        bot.reply_to(message, "❌ Sahifa ma'lumoti topilmadi!", reply_markup=create_admin_menu())
        return
    
    current_page = contact_data[message.from_user.id]['users_page']
    users_per_page = 15
    
    if message.text == "⬅️ Oldingi":
        new_page = max(0, current_page - 1)
    else:  # "➡️ Keyingi"
        total_pages = (len(data['users']) + users_per_page - 1) // users_per_page
        new_page = min(total_pages - 1, current_page + 1)
    
    contact_data[message.from_user.id]['users_page'] = new_page
    
    start_index = new_page * users_per_page
    end_index = start_index + users_per_page
    page_users = data['users'][start_index:end_index]
    
    total_pages = (len(data['users']) + users_per_page - 1) // users_per_page
    
    users_text = f"""
👥 **Barcha Foydalanuvchilar**

📊 **Jami:** {len(data['users'])} ta foydalanuvchi
📄 **Sahifa:** {new_page + 1}/{total_pages}

"""
    
    for i, user in enumerate(page_users, start_index + 1):
        username = user.get('username', 'Noma lum')
        first_name = user.get('first_name', 'Noma lum')
        last_name = user.get('last_name', '')
        user_id = user.get('user_id', 'Noma lum')
        joined_date = user.get('joined_date', 'Noma lum')
        
        full_name = f"{first_name} {last_name}".strip() if last_name else first_name
        
        users_text += f"""
{i}. 👤 {full_name}
   🆔 ID: {user_id}
   📧 @{username}
   📅 {joined_date}
"""
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    
    if total_pages > 1:
        if new_page > 0:
            markup.add(KeyboardButton("⬅️ Oldingi"))
        if new_page < total_pages - 1:
            markup.add(KeyboardButton("➡️ Keyingi"))
    
    markup.add(
        KeyboardButton("🔙 Orqaga"),
        KeyboardButton("📊 Foydalanuvchi statistikasi")
    )
    
    bot.reply_to(message, users_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📊 Foydalanuvchi statistikasi")
def admin_users_stats_button(message):
    """Foydalanuvchi statistikasi"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    if not data['users']:
        bot.reply_to(message, "👥 Hali foydalanuvchilar yo'q!", reply_markup=create_admin_menu())
        return
    
    # Statistika hisoblash
    total_users = len(data['users'])
    
    # Bugungi foydalanuvchilar
    from datetime import datetime, timedelta
    today = datetime.now().strftime("%Y-%m-%d")
    today_users = len([u for u in data['users'] if u.get('joined_date', '').startswith(today)])
    
    # O'tgan hafta foydalanuvchilari
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    week_users = len([u for u in data['users'] if u.get('joined_date', '') >= week_ago])
    
    # O'tgan oy foydalanuvchilari
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    month_users = len([u for u in data['users'] if u.get('joined_date', '') >= month_ago])
    
    # Username bilan foydalanuvchilar
    users_with_username = len([u for u in data['users'] if u.get('username') and u.get('username') != 'Noma lum'])
    
    stats_text = f"""
📊 **Foydalanuvchi Statistikasi**

👥 **Jami foydalanuvchilar:** {total_users} ta

📅 **Vaqt bo'yicha:**
• Bugun: {today_users} ta
• O'tgan hafta: {week_users} ta
• O'tgan oy: {month_users} ta

📧 **Username bilan:** {users_with_username} ta
📧 **Username siz:** {total_users - users_with_username} ta

📈 **O'rtacha kunlik:** {round(month_users / 30, 1)} ta
    """
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("👥 Barcha foydalanuvchilar"),
        KeyboardButton("📋 Foydalanuvchi qidirish"),
        KeyboardButton("🔙 Orqaga")
    )
    
    bot.reply_to(message, stats_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📋 Foydalanuvchi qidirish")
def admin_search_users_button(message):
    """Foydalanuvchi qidirish"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        KeyboardButton("🔍 Ism bo'yicha"),
        KeyboardButton("🔍 Username bo'yicha"),
        KeyboardButton("🔍 ID bo'yicha"),
        KeyboardButton("🔙 Orqaga")
    )
    
    bot.reply_to(message, 
                 "📋 **Foydalanuvchi qidirish**\n\n"
                 "Qanday usulda qidirmoqchisiz?",
                 reply_markup=markup)
    
    user_states[message.from_user.id] = "admin_search_users_method"

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_search_users_method")
def handle_admin_search_users_method(message):
    """Foydalanuvchi qidirish usulini tanlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Orqaga":
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("👥 Barcha foydalanuvchilar"),
            KeyboardButton("📊 Foydalanuvchi statistikasi"),
            KeyboardButton("🗑️ Foydalanuvchi o'chirish"),
            KeyboardButton("📋 Foydalanuvchi qidirish"),
            KeyboardButton("🔙 Orqaga")
        )
        
        bot.reply_to(message, "❌ Qidirish bekor qilindi.", reply_markup=markup)
        return
    
    search_method = message.text.strip()
    
    if search_method == "🔍 Ism bo'yicha":
        user_states[message.from_user.id] = "admin_search_users_name"
        bot.reply_to(message, "🔍 Foydalanuvchi ismini yozing:")
    elif search_method == "🔍 Username bo'yicha":
        user_states[message.from_user.id] = "admin_search_users_username"
        bot.reply_to(message, "🔍 Username yozing (@ belgisiz):")
    elif search_method == "🔍 ID bo'yicha":
        user_states[message.from_user.id] = "admin_search_users_id"
        bot.reply_to(message, "🔍 Foydalanuvchi ID sini yozing:")
    else:
        bot.reply_to(message, "❌ Noto'g'ri tanlov! Iltimos, qayta tanlang.")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_search_users_name")
def handle_admin_search_users_name(message):
    """Ism bo'yicha foydalanuvchi qidirish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    search_term = message.text.strip().lower()
    found_users = []
    
    for user in data['users']:
        first_name = user.get('first_name', '') or ''
        last_name = user.get('last_name', '') or ''
        
        first_name_lower = first_name.lower()
        last_name_lower = last_name.lower()
        full_name = f"{first_name} {last_name}".strip()
        full_name_lower = full_name.lower()
        
        if search_term in first_name_lower or search_term in last_name_lower or search_term in full_name_lower:
            found_users.append(user)
    
    if not found_users:
        bot.reply_to(message, f"❌ '{message.text}' ismli foydalanuvchi topilmadi!", reply_markup=create_admin_menu())
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        return
    
    users_text = f"""
🔍 **Qidiruv natijalari**

📝 **Qidiruv so'zi:** {message.text}
📊 **Topilgan:** {len(found_users)} ta foydalanuvchi

"""
    
    for i, user in enumerate(found_users, 1):
        username = user.get('username', 'Noma lum')
        first_name = user.get('first_name', 'Noma lum')
        last_name = user.get('last_name', '')
        user_id = user.get('user_id', 'Noma lum')
        joined_date = user.get('joined_date', 'Noma lum')
        
        full_name = f"{first_name} {last_name}".strip() if last_name else first_name
        
        users_text += f"""
{i}. 👤 {full_name}
   🆔 ID: {user_id}
   📧 @{username}
   📅 {joined_date}
"""
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("👥 Barcha foydalanuvchilar"),
        KeyboardButton("📋 Foydalanuvchi qidirish"),
        KeyboardButton("🔙 Orqaga")
    )
    
    bot.reply_to(message, users_text, reply_markup=markup)
    
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_search_users_username")
def handle_admin_search_users_username(message):
    """Username bo'yicha foydalanuvchi qidirish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    search_term = message.text.strip().lower()
    found_users = []
    
    for user in data['users']:
        username = user.get('username', '') or ''
        username_lower = username.lower()
        if search_term in username_lower:
            found_users.append(user)
    
    if not found_users:
        bot.reply_to(message, f"❌ '@{message.text}' username li foydalanuvchi topilmadi!", reply_markup=create_admin_menu())
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        return
    
    users_text = f"""
🔍 **Qidiruv natijalari**

📝 **Qidiruv so'zi:** @{message.text}
📊 **Topilgan:** {len(found_users)} ta foydalanuvchi

"""
    
    for i, user in enumerate(found_users, 1):
        username = user.get('username', 'Noma lum')
        first_name = user.get('first_name', 'Noma lum')
        last_name = user.get('last_name', '')
        user_id = user.get('user_id', 'Noma lum')
        joined_date = user.get('joined_date', 'Noma lum')
        
        full_name = f"{first_name} {last_name}".strip() if last_name else first_name
        
        users_text += f"""
{i}. 👤 {full_name}
   🆔 ID: {user_id}
   📧 @{username}
   📅 {joined_date}
"""
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("👥 Barcha foydalanuvchilar"),
        KeyboardButton("📋 Foydalanuvchi qidirish"),
        KeyboardButton("🔙 Orqaga")
    )
    
    bot.reply_to(message, users_text, reply_markup=markup)
    
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_search_users_id")
def handle_admin_search_users_id(message):
    """ID bo'yicha foydalanuvchi qidirish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        search_id = int(message.text.strip())
        found_users = []
        
        for user in data['users']:
            user_id = user.get('user_id')
            if user_id and str(user_id) == str(search_id):
                found_users.append(user)
                break
        
        if not found_users:
            bot.reply_to(message, f"❌ ID: {message.text} foydalanuvchi topilmadi!", reply_markup=create_admin_menu())
            if message.from_user.id in user_states:
                del user_states[message.from_user.id]
            return
        
        user = found_users[0]
        username = user.get('username', 'Noma lum')
        first_name = user.get('first_name', 'Noma lum')
        last_name = user.get('last_name', '')
        user_id = user.get('user_id', 'Noma lum')
        joined_date = user.get('joined_date', 'Noma lum')
        
        full_name = f"{first_name} {last_name}".strip() if last_name else first_name
        
        users_text = f"""
🔍 **Qidiruv natijalari**

📝 **Qidiruv ID:** {message.text}
📊 **Topilgan:** 1 ta foydalanuvchi

👤 **Foydalanuvchi ma'lumotlari:**
• Ism: {full_name}
• ID: {user_id}
• Username: @{username}
• Ro'yxatdan o'tgan: {joined_date}
"""
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("👥 Barcha foydalanuvchilar"),
            KeyboardButton("📋 Foydalanuvchi qidirish"),
            KeyboardButton("🔙 Orqaga")
        )
        
        bot.reply_to(message, users_text, reply_markup=markup)
        
    except ValueError:
        bot.reply_to(message, "❌ Noto'g'ri ID! Iltimos, raqam kiriting.")
        return
    
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]

@bot.message_handler(func=lambda message: message.text == "🗑️ Foydalanuvchi o'chirish")
def admin_delete_user_button(message):
    """Foydalanuvchi o'chirish"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    if not data['users']:
        bot.reply_to(message, "👥 Hali foydalanuvchilar yo'q!", reply_markup=create_admin_menu())
        return
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        KeyboardButton("🔍 ID bo'yicha o'chirish"),
        KeyboardButton("🔍 Username bo'yicha o'chirish"),
        KeyboardButton("🗑️ Oxirgi foydalanuvchini o'chirish"),
        KeyboardButton("🔙 Orqaga")
    )
    
    bot.reply_to(message, 
                 "🗑️ **Foydalanuvchi o'chirish**\n\n"
                 "Qanday usulda o'chirmoqchisiz?",
                 reply_markup=markup)
    
    user_states[message.from_user.id] = "admin_delete_user_method"

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_delete_user_method")
def handle_admin_delete_user_method(message):
    """Foydalanuvchi o'chirish usulini tanlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Orqaga":
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("👥 Barcha foydalanuvchilar"),
            KeyboardButton("📊 Foydalanuvchi statistikasi"),
            KeyboardButton("🗑️ Foydalanuvchi o'chirish"),
            KeyboardButton("📋 Foydalanuvchi qidirish"),
            KeyboardButton("🔙 Orqaga")
        )
        
        bot.reply_to(message, "❌ O'chirish bekor qilindi.", reply_markup=markup)
        return
    
    delete_method = message.text.strip()
    
    if delete_method == "🔍 ID bo'yicha o'chirish":
        user_states[message.from_user.id] = "admin_delete_user_id"
        bot.reply_to(message, "🔍 O'chiriladigan foydalanuvchi ID sini yozing:")
    elif delete_method == "🔍 Username bo'yicha o'chirish":
        user_states[message.from_user.id] = "admin_delete_user_username"
        bot.reply_to(message, "🔍 O'chiriladigan foydalanuvchi username ini yozing (@ belgisiz):")
    elif delete_method == "🗑️ Oxirgi foydalanuvchini o'chirish":
        # Oxirgi foydalanuvchini o'chirish
        if data['users']:
            deleted_user = data['users'].pop()
            save_data(data)
            
            username = deleted_user.get('username', 'Noma lum')
            first_name = deleted_user.get('first_name', 'Noma lum')
            last_name = deleted_user.get('last_name', '')
            user_id = deleted_user.get('user_id', 'Noma lum')
            
            full_name = f"{first_name} {last_name}".strip() if last_name else first_name
            
            success_text = f"""
✅ Oxirgi foydalanuvchi muvaffaqiyatli o'chirildi!

👤 **O'chirilgan foydalanuvchi:**
• Ism: {full_name}
• ID: {user_id}
• Username: @{username}

📊 **Qolgan foydalanuvchilar:** {len(data['users'])} ta
            """
            
            bot.reply_to(message, success_text, reply_markup=create_admin_menu())
        else:
            bot.reply_to(message, "❌ O'chiriladigan foydalanuvchi yo'q!", reply_markup=create_admin_menu())
        
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
    else:
        bot.reply_to(message, "❌ Noto'g'ri tanlov! Iltimos, qayta tanlang.")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_delete_user_id")
def handle_admin_delete_user_id(message):
    """ID bo'yicha foydalanuvchi o'chirish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        delete_id = int(message.text.strip())
        deleted_user = None
        user_index = -1
        
        for i, user in enumerate(data['users']):
            user_id = user.get('user_id')
            if user_id and str(user_id) == str(delete_id):
                deleted_user = data['users'].pop(i)
                user_index = i
                break
        
        if not deleted_user:
            bot.reply_to(message, f"❌ ID: {message.text} foydalanuvchi topilmadi!", reply_markup=create_admin_menu())
            if message.from_user.id in user_states:
                del user_states[message.from_user.id]
            return
        
        # data.json ga saqlash
        save_data(data)
        
        username = deleted_user.get('username', 'Noma lum')
        first_name = deleted_user.get('first_name', 'Noma lum')
        last_name = deleted_user.get('last_name', '')
        user_id = deleted_user.get('user_id', 'Noma lum')
        
        full_name = f"{first_name} {last_name}".strip() if last_name else first_name
        
        success_text = f"""
✅ Foydalanuvchi muvaffaqiyatli o'chirildi!

👤 **O'chirilgan foydalanuvchi:**
• Ism: {full_name}
• ID: {user_id}
• Username: @{username}

📊 **Qolgan foydalanuvchilar:** {len(data['users'])} ta
        """
        
        bot.reply_to(message, success_text, reply_markup=create_admin_menu())
        
    except ValueError:
        bot.reply_to(message, "❌ Noto'g'ri ID! Iltimos, raqam kiriting.")
        return
    
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_delete_user_username")
def handle_admin_delete_user_username(message):
    """Username bo'yicha foydalanuvchi o'chirish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    search_term = message.text.strip().lower()
    deleted_user = None
    user_index = -1
    
    for i, user in enumerate(data['users']):
        username = user.get('username', '') or ''
        username_lower = username.lower()
        if search_term == username_lower:
            deleted_user = data['users'].pop(i)
            user_index = i
            break
    
    if not deleted_user:
        bot.reply_to(message, f"❌ '@{message.text}' username li foydalanuvchi topilmadi!", reply_markup=create_admin_menu())
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        return
    
    # data.json ga saqlash
    save_data(data)
    
    username = deleted_user.get('username', 'Noma lum')
    first_name = deleted_user.get('first_name', 'Noma lum')
    last_name = deleted_user.get('last_name', '')
    user_id = deleted_user.get('user_id', 'Noma lum')
    
    full_name = f"{first_name} {last_name}".strip() if last_name else first_name
    
    success_text = f"""
✅ Foydalanuvchi muvaffaqiyatli o'chirildi!

👤 **O'chirilgan foydalanuvchi:**
• Ism: {full_name}
• ID: {user_id}
• Username: @{username}

📊 **Qolgan foydalanuvchilar:** {len(data['users'])} ta
    """
    
    bot.reply_to(message, success_text, reply_markup=create_admin_menu())
    
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]

@bot.message_handler(func=lambda message: message.text == "⚙️ Sozlamalar")
def admin_settings_button(message):
    """Admin sozlamalar tugmasini bosganda"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    settings_text = f"""
⚙️ **Bot Sozlamalari**

🔑 **Bot Token:** {data['settings']['bot_token']}
👤 **Admin ID:** {data['settings']['admin_id']}

💳 **To'lov ma'lumotlari:**
🏦 Karta raqam: {data['settings']['payment_card']}
👤 Mulkdor: {data['settings']['payment_owner']}
🏛️ Bank: {data['settings']['payment_bank']}
    """
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🔑 Token o'zgartirish"),
        KeyboardButton("👤 Admin ID o'zgartirish"),
        KeyboardButton("💳 To'lov ma'lumotlari"),
        KeyboardButton("🔙 Orqaga")
    )
    
    bot.reply_to(message, settings_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🗑️ Hammasini o'chirish")
def admin_delete_all_button(message):
    """Hammasini o'chirish tugmasini bosganda"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    # Tasdiqlash so'rash
    warning_text = """
⚠️ **OGOHLANTIRISH!**

Siz barcha kategoriyalar va mahsulotlarni o'chirmoqchisiz!

Bu amal qaytarib bo'lmaydi va barcha ma'lumotlar yo'qoladi:
🗑️ Barcha kategoriyalar
🗑️ Barcha mahsulotlar
🗑️ Barcha buyurtmalar
🗑️ Barcha foydalanuvchilar

Davom etishni xohlaysizmi?
    """
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("✅ Ha, hammasini o'chir"),
        KeyboardButton("❌ Yo'q, bekor qil"),
        KeyboardButton("🔙 Orqaga")
    )
    
    bot.reply_to(message, warning_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "✅ Ha, hammasini o'chir")
def admin_confirm_delete_all(message):
    """Hammasini o'chirishni tasdiqlash"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    try:
        # Barcha ma'lumotlarni o'chirish
        data['categories'] = {}
        data['orders'] = []
        data['users'] = []
        
        # data.json ga saqlash
        save_data(data)
        
        # Mahsulotlarni yangilash
        update_products()
        
        success_text = """
✅ **Barcha ma'lumotlar o'chirildi!**

🗑️ Kategoriyalar: O'chirildi
🗑️ Mahsulotlar: O'chirildi  
🗑️ Buyurtmalar: O'chirildi
🗑️ Foydalanuvchilar: O'chirildi

Bot endi tozalangan va yangi ma'lumotlar qo'shishga tayyor!
        """
        
        bot.reply_to(message, success_text, reply_markup=create_admin_menu())
        
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik yuz berdi: {e}", reply_markup=create_admin_menu())

@bot.message_handler(func=lambda message: message.text == "❌ Yo'q, bekor qil")
def admin_cancel_delete_all(message):
    """Hammasini o'chirishni bekor qilish"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    bot.reply_to(message, "✅ O'chirish bekor qilindi! Ma'lumotlar xavfsiz.", reply_markup=create_admin_menu())

# Orqaga qaytish tugmalari
@bot.message_handler(func=lambda message: message.text == "🔙 Orqaga")
def admin_back_button(message):
    """Admin orqaga qaytish tugmasini bosganda"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    # Agar o'chirish jarayonida bo'lsa, bekor qilish
    if message.text == "🔙 Orqaga":
        admin_text = """
🔧 **Admin Panel**

Quyidagi funksiyalardan birini tanlang:
📊 Statistika - umumiy ma'lumotlar
📦 Mahsulotlar - mahsulotlarni boshqarish
🏷️ Kategoriyalar - kategoriyalarni boshqarish
📋 Buyurtmalar - buyurtmalarni ko'rish
👥 Foydalanuvchilar - foydalanuvchilar ro'yxati
⚙️ Sozlamalar - bot sozlamalari
🗑️ Hammasini o'chirish - barcha ma'lumotlarni o'chirish
        """
        
        bot.reply_to(message, admin_text, reply_markup=create_admin_menu())

# Mahsulot qo'shish tugmasi
@bot.message_handler(func=lambda message: message.text == "➕ Mahsulot qo'shish")
def admin_add_product_button(message):
    """Mahsulot qo'shish tugmasini bosganda"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    # Kategoriyalar ro'yxatini ko'rsatish
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    for category_key, category_data in data['categories'].items():
        emoji = category_data.get('emoji', '📦')
        name = category_data['name']
        markup.add(KeyboardButton(f"{emoji} {name}"))
    
    markup.add(KeyboardButton("🔙 Orqaga"))
    
    bot.reply_to(message, 
                 "📦 Yangi mahsulot qo'shish\n\n"
                 "Qaysi kategoriyaga qo'shmoqchisiz?\n"
                 "Kategoriya nomini yozing:",
                 reply_markup=markup)
    
    user_states[message.from_user.id] = "admin_add_product_category"

# Mahsulot tahrirlash tugmasi
@bot.message_handler(func=lambda message: message.text == "✏️ Mahsulot tahrirlash")
def admin_edit_product_button(message):
    """Mahsulot tahrirlash tugmasini bosganda"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    # Kategoriyalar ro'yxatini ko'rsatish
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    for category_key, category_data in data['categories'].items():
        emoji = category_data.get('emoji', '📦')
        name = category_data['name']
        product_count = len(category_data['products'])
        if product_count > 0:
            markup.add(KeyboardButton(f"{emoji} {name} ({product_count} ta mahsulot)"))
    
    markup.add(KeyboardButton("🔙 Orqaga"))
    
    bot.reply_to(message, 
                 "✏️ Qaysi kategoriyadan mahsulot tahrirlamoqchisiz?\n\n"
                 "Kategoriya nomini yozing:",
                 reply_markup=markup)
    
    user_states[message.from_user.id] = "admin_edit_product_category"

# Kategoriya qo'shish tugmasi
@bot.message_handler(func=lambda message: message.text == "➕ Kategoriya qo'shish")
def admin_add_category_button(message):
    """Kategoriya qo'shish tugmasini bosganda"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    user_states[message.from_user.id] = "admin_add_category_name"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.reply_to(message, 
                 "🏷️ Yangi kategoriya qo'shish\n\n"
                 "Kategoriya nomini yozing (masalan: Elektronika):",
                 reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📁 Ichki kategoriya qo'shish")
def admin_add_subcategory_button(message):
    """Ichki kategoriya qo'shish tugmasini bosganda"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    if not data['categories']:
        bot.reply_to(message, "❌ Avval asosiy kategoriya qo'shishingiz kerak!", reply_markup=create_admin_menu())
        return
    
    # Kategoriyalar ro'yxatini ko'rsatish
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    for category_key, category_data in data['categories'].items():
        emoji = category_data.get('emoji', '📦')
        name = category_data['name']
        markup.add(KeyboardButton(f"{emoji} {name}"))
    
    markup.add(KeyboardButton("🔙 Orqaga"))
    
    bot.reply_to(message, 
                 "📁 Yangi ichki kategoriya qo'shish\n\n"
                 "Qaysi kategoriyaga ichki kategoriya qo'shmoqchisiz?\n"
                 "Kategoriya nomini tanlang:",
                 reply_markup=markup)
    
    user_states[message.from_user.id] = "admin_add_subcategory_category"

# Kategoriya o'chirish tugmasi
@bot.message_handler(func=lambda message: message.text == "🗑️ Kategoriya o'chirish")
def admin_delete_category_button(message):
    """Kategoriya o'chirish tugmasini bosganda"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    if not data['categories']:
        bot.reply_to(message, "❌ O'chiriladigan kategoriyalar yo'q!", reply_markup=create_admin_menu())
        return
    
    # Kategoriyalar ro'yxatini ko'rsatish
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    for category_key, category_data in data['categories'].items():
        emoji = category_data.get('emoji', '📦')
        name = category_data['name']
        product_count = len(category_data['products'])
        markup.add(KeyboardButton(f"🗑️ {emoji} {name} ({product_count} ta mahsulot)"))
    
    markup.add(KeyboardButton("🔙 Orqaga"))
    
    bot.reply_to(message, 
                 "🗑️ Qaysi kategoriyani o'chirmoqchisiz?\n\n"
                 "⚠️ Kategoriya bilan birga undagi barcha mahsulotlar ham o'chadi!",
                 reply_markup=markup)
    
    user_states[message.from_user.id] = "admin_delete_category"

# Mahsulot o'chirish tugmasi
@bot.message_handler(func=lambda message: message.text == "🗑️ Mahsulot o'chirish")
def admin_delete_product_button(message):
    """Mahsulot o'chirish tugmasini bosganda"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Siz admin emassiz!")
        return
    
    # Kategoriyalar ro'yxatini ko'rsatish
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    for category_key, category_data in data['categories'].items():
        emoji = category_data.get('emoji', '📦')
        name = category_data['name']
        product_count = len(category_data['products'])
        if product_count > 0:
            markup.add(KeyboardButton(f"{emoji} {name} ({product_count} ta mahsulot)"))
    
    markup.add(KeyboardButton("🔙 Orqaga"))
    
    bot.reply_to(message, 
                 "🗑️ Qaysi kategoriyadan mahsulot o'chirmoqchisiz?",
                 reply_markup=markup)
    
    user_states[message.from_user.id] = "admin_delete_product_category"

@bot.message_handler(func=lambda message: message.text == "📞 Aloqa")
def start_contact(message):
    """Aloqa boshlash"""
    user_id = message.from_user.id
    user_states[user_id] = "waiting_phone"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("📱 Raqamingizni yuboring", request_contact=True))
    markup.add(KeyboardButton("🔙 Asosiy menyu"))
    
    bot.reply_to(message, 
                 "📞 Aloqa uchun avval telefon raqamingizni kiriting:\n\n"
                 "Pastdagi tugmani bosing yoki raqamingizni yozing:",
                 reply_markup=markup)

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    """Contact yuborilganda"""
    user_id = message.from_user.id
    
    if user_states.get(user_id) == "waiting_phone":
        phone = message.contact.phone_number
        print(f"Contact received: {phone}")
        
        # Raqamni saqlash
        if user_id not in contact_data:
            contact_data[user_id] = {}
        contact_data[user_id]['phone'] = phone
        
        # Keyingi bosqichga o'tish
        user_states[user_id] = "waiting_question"
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add(KeyboardButton("🔙 Asosiy menyu"))
        
        bot.reply_to(message, 
                     f"✅ Telefon raqamingiz qabul qilindi: {phone}\n\n"
                     "📝 Endi savolingizni yuboring:",
                     reply_markup=markup)
    
    elif user_states.get(user_id) == "waiting_phone_checkout":
        phone = message.contact.phone_number
        print(f"Checkout contact received: {phone}")
        
        # Telefon raqamni saqlash
        contact_data[user_id]['checkout_data']['phone'] = phone
        user_states[user_id] = "waiting_address"
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add(KeyboardButton("📍 Manzilni yuboring", request_location=True))
        markup.add(KeyboardButton("🔙 Bekor qilish"))
        
        bot.reply_to(message, 
                     f"✅ Telefon raqam: {phone}\n\n"
                     "📍 Endi manzilingizni kiriting:",
                     reply_markup=markup)

@bot.message_handler(content_types=['location'])
def handle_location(message):
    """Location yuborilganda"""
    user_id = message.from_user.id
    print(f"Location received from user {user_id}, state: {user_states.get(user_id)}")
    
    if user_states.get(user_id) == "waiting_payment_approval":
        location = message.location
        print(f"Location after payment received: {location.latitude}, {location.longitude}")
        
        # Lokatsiyani adminga yuborish
        if user_id in contact_data and 'pending_order' in contact_data[user_id]:
            pending_order = contact_data[user_id]['pending_order']
            
            location_message = f"""
📍 Mijoz lokatsiyasi!

👤 Mijoz: {pending_order['customer_name']}
📱 Telefon: {pending_order['customer_phone']}
📍 Lokatsiya: {location.latitude}, {location.longitude}
💰 To'lov miqdori: {pending_order['total']:,} so'm
📦 Mahsulotlar: {', '.join(pending_order['items'])}

🗺️ Xaritada ko'rish: https://maps.google.com/?q={location.latitude},{location.longitude}
            """
            
            try:
                # Lokatsiyani saqlash
                contact_data[user_id]['pending_order']['location'] = {
                    'latitude': location.latitude,
                    'longitude': location.longitude
                }
                print(f"Location saved: {contact_data[user_id]['pending_order']['location']}")
                
                # Lokatsiyani xarita ko'rinishida yuborish
                bot.send_location(
                    ADMIN_ID,
                    latitude=location.latitude,
                    longitude=location.longitude
                )
                
                # Keyin matn ma'lumotlarini yuborish
                bot.send_message(ADMIN_ID, location_message)
                print("Location sent to admin successfully")
                
                # Foydalanuvchiga tasdiq
                bot.reply_to(message, 
                             "✅ Lokatsiya yuborildi!\n\n"
                             "⏳ Admin tekshirishni kutyapti...")
                
                # Foydalanuvchi holatini o'zgartirish
                user_states[user_id] = "waiting_admin_approval"
                
            except Exception as e:
                print(f"Error sending location to admin: {e}")
                bot.reply_to(message, f"❌ Xatolik yuz berdi: {e}")
        else:
            bot.reply_to(message, "❌ Buyurtma ma'lumotlari topilmadi!")
    
    elif user_states.get(user_id) == "waiting_address":
        location = message.location
        print(f"Location for address received: {location.latitude}, {location.longitude}")
        
        # Manzilni saqlash
        address = f"Latitude: {location.latitude}, Longitude: {location.longitude}"
        contact_data[user_id]['checkout_data']['address'] = address
        
        # Foydalanuvchi ma'lumotlarini olish
        user_info = message.from_user
        customer_name = f"{user_info.first_name} {user_info.last_name or ''}".strip()
        customer_phone = contact_data[user_id]['checkout_data'].get('phone', 'Noma lum')
        
        # Lokatsiyani admin panelga yuborish
        admin_location_message = f"""
📍 **Yangi buyurtma lokatsiyasi!**

👤 **Mijoz:** {customer_name}
📱 **Telefon:** {customer_phone}
📍 **Lokatsiya:** {location.latitude}, {location.longitude}
💰 **To'lov miqdori:** {contact_data[user_id]['checkout_data'].get('total', 0):,} so'm

🗺️ **Xaritada ko'rish:** https://maps.google.com/?q={location.latitude},{location.longitude}
        """
        
        try:
            # Lokatsiyani xarita ko'rinishda yuborish
            bot.send_location(
                ADMIN_ID,
                latitude=location.latitude,
                longitude=location.longitude
            )
            
            # Keyin matn ma'lumotlarini yuborish
            bot.send_message(ADMIN_ID, admin_location_message)
            print("Location sent to admin successfully")
            
        except Exception as e:
            print(f"Error sending location to admin: {e}")
        
        user_states[user_id] = "waiting_payment"
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("💳 Karta bilan to'lov", callback_data="payment_card"),
            InlineKeyboardButton("💵 Naqd pul", callback_data="payment_cash")
        )
        
        bot.reply_to(message, 
                     f"✅ Manzil qabul qilindi!\n\n"
                     "💳 Tolov usulini tanlang:",
                     reply_markup=markup)
    
    else:
        # Agar boshqa holatda lokatsiya yuborilsa
        bot.reply_to(message, "❌ Lokatsiya yuborish vaqti emas!")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_phone")
def handle_phone_input(message):
    """Telefon raqamini qabul qilish (qo'lda yozilgan)"""
    user_id = message.from_user.id
    
    # Foydalanuvchi qo'lda raqam yozdi
    phone = message.text
    print(f"Manual input: {phone}")
    
    # Raqamni tozalash va tekshirish
    phone = phone.strip()
    
    # Raqam formatini tekshirish
    if not phone or len(phone) < 7:
        bot.reply_to(message, 
                     "❌ Noto'g'ri telefon raqam! Iltimos, to'g'ri raqam kiriting.\n\n"
                     "Masalan: +998901234567 yoki 901234567")
        return
    
    # Raqamni saqlash
    if user_id not in contact_data:
        contact_data[user_id] = {}
    contact_data[user_id]['phone'] = phone
    
    # Keyingi bosqichga o'tish
    user_states[user_id] = "waiting_question"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("🔙 Asosiy menyu"))
    
    bot.reply_to(message, 
                 f"✅ Telefon raqamingiz qabul qilindi: {phone}\n\n"
                 "📝 Endi savolingizni yuboring:",
                 reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_name")
def handle_name_input(message):
    """Ism va familiyani qabul qilish"""
    user_id = message.from_user.id
    
    if message.text == "🔙 Bekor qilish":
        # Bekor qilish
        if user_id in user_states:
            del user_states[user_id]
        if user_id in contact_data and 'checkout_data' in contact_data[user_id]:
            del contact_data[user_id]['checkout_data']
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("🛍️ Kategoriyalar"),
            KeyboardButton("🔍 Qidiruv"),
            KeyboardButton("🛒 Savat"),
            KeyboardButton("🌐 Til"),
            KeyboardButton("📋 Buyurtmalar"),
            KeyboardButton("📞 Aloqa")
        )
        
        bot.reply_to(message, "❌ Buyurtma bekor qilindi.", reply_markup=markup)
        return
    
    # Ism va familiyani saqlash
    contact_data[user_id]['checkout_data']['name'] = message.text
    user_states[user_id] = "waiting_phone_checkout"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("📱 Raqamingizni yuboring", request_contact=True))
    markup.add(KeyboardButton("🔙 Bekor qilish"))
    
    bot.reply_to(message, 
                 f"✅ Ism va familiya: {message.text}\n\n"
                 "📱 Endi telefon raqamingizni kiriting:",
                 reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_phone_checkout")
def handle_phone_checkout_input(message):
    """Buyurtma uchun telefon raqamini qabul qilish"""
    user_id = message.from_user.id
    
    if message.text == "🔙 Bekor qilish":
        # Bekor qilish
        if user_id in user_states:
            del user_states[user_id]
        if user_id in contact_data and 'checkout_data' in contact_data[user_id]:
            del contact_data[user_id]['checkout_data']
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("🛍️ Kategoriyalar"),
            KeyboardButton("🔍 Qidiruv"),
            KeyboardButton("🛒 Savat"),
            KeyboardButton("🌐 Til"),
            KeyboardButton("📋 Buyurtmalar"),
            KeyboardButton("📞 Aloqa")
        )
        
        bot.reply_to(message, "❌ Buyurtma bekor qilindi.", reply_markup=markup)
        return
    
    phone = ""
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text.strip()
    
    if not phone or len(phone) < 7:
        bot.reply_to(message, "❌ Noto'g'ri telefon raqam! Iltimos, to'g'ri raqam kiriting.")
        return
    
    # Telefon raqamni saqlash
    contact_data[user_id]['checkout_data']['phone'] = phone
    user_states[user_id] = "waiting_address"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("📍 Manzilni yuboring", request_location=True))
    markup.add(KeyboardButton("🔙 Bekor qilish"))
    
    bot.reply_to(message, 
                 f"✅ Telefon raqam: {phone}\n\n"
                 "📍 Endi manzilingizni kiriting:",
                 reply_markup=markup)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """Rasm yuborilganda"""
    user_id = message.from_user.id
    print(f"Photo received from user {user_id}, state: {user_states.get(user_id)}")
    
    if user_states.get(user_id) == "waiting_payment_screenshot":
        print("Processing payment screenshot")
        handle_payment_screenshot_logic(message)
    else:
        print(f"Photo received but not in payment state. Current state: {user_states.get(user_id)}")

def handle_payment_screenshot_logic(message):
    """To'lov chekini qabul qilish"""
    user_id = message.from_user.id
    print(f"Payment screenshot received from user {user_id}")
    
    if message.text == "🔙 Bekor qilish":
        # Bekor qilish
        if user_id in user_states:
            del user_states[user_id]
        if user_id in contact_data and 'pending_order' in contact_data[user_id]:
            del contact_data[user_id]['pending_order']
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("🛍️ Kategoriyalar"),
            KeyboardButton("🔍 Qidiruv"),
            KeyboardButton("🛒 Savat"),
            KeyboardButton("🌐 Til"),
            KeyboardButton("📋 Buyurtmalar"),
            KeyboardButton("📞 Aloqa")
        )
        
        bot.reply_to(message, "❌ To'lov bekor qilindi.", reply_markup=markup)
        return
    
    print(f"Photo received: {len(message.photo)} photos")
    
    # Skrinshotni adminga yuborish
    if user_id not in contact_data or 'pending_order' not in contact_data[user_id]:
        bot.reply_to(message, "❌ Buyurtma ma'lumotlari topilmadi!")
        return
    
    pending_order = contact_data[user_id]['pending_order']
    print(f"Pending order found: {pending_order}")
    
    admin_message = f"""
💳 Yangi to'lov cheki!

👤 Mijoz: {pending_order['customer_name']}
📱 Telefon: {pending_order['customer_phone']}
📍 Manzil: {pending_order['customer_address']}
💰 To'lov miqdori: {pending_order['total']:,} so'm
📦 Mahsulotlar: {', '.join(pending_order['items'])}
    """
    
    # Admin uchun tasdiqlash tugmalari
    admin_markup = InlineKeyboardMarkup(row_width=2)
    admin_markup.add(
        InlineKeyboardButton("✅ Qabul qilish", callback_data=f"approve_payment_{user_id}"),
        InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_payment_{user_id}")
    )
    
    try:
        print(f"Sending to admin {ADMIN_ID}")
        # Skrinshotni adminga yuborish
        bot.send_photo(
            ADMIN_ID,
            message.photo[-1].file_id,
            caption=admin_message,
            reply_markup=admin_markup
        )
        print("Photo sent to admin successfully")
        
        # Foydalanuvchiga tasdiq
        bot.reply_to(message, 
                     "✅ To'lov cheki yuborildi!\n\n"
                     "⏳ Admin tasdiqlashini kuting...",
                     reply_markup=create_main_menu())
        
        # Foydalanuvchi holatini o'zgartirish
        user_states[user_id] = "waiting_payment_approval"
        
    except Exception as e:
        print(f"Error sending to admin: {e}")
        bot.reply_to(message, f"❌ Xatolik yuz berdi: {e}")
        print(f"Admin xabar yuborishda xatolik: {e}")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_payment_screenshot")
def handle_payment_screenshot(message):
    """To'lov chekini qabul qilish"""
    user_id = message.from_user.id
    print(f"Payment screenshot received from user {user_id}")
    
    if message.text == "🔙 Bekor qilish":
        # Bekor qilish
        if user_id in user_states:
            del user_states[user_id]
        if user_id in contact_data and 'pending_order' in contact_data[user_id]:
            del contact_data[user_id]['pending_order']
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("🛍️ Kategoriyalar"),
            KeyboardButton("🔍 Qidiruv"),
            KeyboardButton("🛒 Savat"),
            KeyboardButton("🌐 Til"),
            KeyboardButton("📋 Buyurtmalar"),
            KeyboardButton("📞 Aloqa")
        )
        
        bot.reply_to(message, "❌ To'lov bekor qilindi.", reply_markup=markup)
        return
    
    if not message.photo:
        bot.reply_to(message, "❌ Iltimos, to'lov chekini rasm sifatida yuboring!")
        return
    
    print(f"Photo received: {len(message.photo)} photos")
    
    # Skrinshotni adminga yuborish
    if user_id not in contact_data or 'pending_order' not in contact_data[user_id]:
        bot.reply_to(message, "❌ Buyurtma ma'lumotlari topilmadi!")
        return
    
    pending_order = contact_data[user_id]['pending_order']
    print(f"Pending order found: {pending_order}")
    
    admin_message = f"""
💳 Yangi to'lov cheki!

👤 Mijoz: {pending_order['customer_name']}
📱 Telefon: {pending_order['customer_phone']}
📍 Manzil: {pending_order['customer_address']}
💰 To'lov miqdori: {pending_order['total']:,} so'm
📦 Mahsulotlar: {', '.join(pending_order['items'])}
    """
    
    # Admin uchun tasdiqlash tugmalari
    admin_markup = InlineKeyboardMarkup(row_width=2)
    admin_markup.add(
        InlineKeyboardButton("✅ Qabul qilish", callback_data=f"approve_payment_{user_id}"),
        InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_payment_{user_id}")
    )
    
    try:
        print(f"Sending to admin {ADMIN_ID}")
        # Skrinshotni adminga yuborish
        bot.send_photo(
            ADMIN_ID,
            message.photo[-1].file_id,
            caption=admin_message,
            reply_markup=admin_markup
        )
        print("Photo sent to admin successfully")
        
        # Foydalanuvchiga tasdiq
        bot.reply_to(message, 
                     "✅ To'lov cheki yuborildi!\n\n"
                     "⏳ Admin tasdiqlashini kuting...",
                     reply_markup=create_main_menu())
        
        # Foydalanuvchi holatini o'zgartirish
        user_states[user_id] = "waiting_payment_approval"
        
    except Exception as e:
        print(f"Error sending to admin: {e}")
        bot.reply_to(message, f"❌ Xatolik yuz berdi: {e}")
        print(f"Admin xabar yuborishda xatolik: {e}")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_address")
def handle_address_input(message):
    """Manzilni qabul qilish"""
    user_id = message.from_user.id
    
    if message.text == "🔙 Bekor qilish":
        # Bekor qilish
        if user_id in user_states:
            del user_states[user_id]
        if user_id in contact_data and 'checkout_data' in contact_data[user_id]:
            del contact_data[user_id]['checkout_data']
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("🛍️ Kategoriyalar"),
            KeyboardButton("🔍 Qidiruv"),
            KeyboardButton("🛒 Savat"),
            KeyboardButton("🌐 Til"),
            KeyboardButton("📋 Buyurtmalar"),
            KeyboardButton("📞 Aloqa")
        )
        
        bot.reply_to(message, "❌ Buyurtma bekor qilindi.", reply_markup=markup)
        return
    
    # Manzilni saqlash
    contact_data[user_id]['checkout_data']['address'] = message.text
    user_states[user_id] = "waiting_payment"
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💳 Karta bilan to'lov", callback_data="payment_card"),
        InlineKeyboardButton("💵 Naqd pul", callback_data="payment_cash")
    )
    
    bot.reply_to(message, 
                 f"✅ Manzil: {message.text}\n\n"
                 "💳 Tolov usulini tanlang:",
                 reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_quantity")
def handle_quantity_input(message):
    """Miqdorni qabul qilish va savatga qo'shish"""
    user_id = message.from_user.id
    
    if message.text == "🔙 Orqaga":
        # Orqaga qaytish
        if user_id in user_states:
            del user_states[user_id]
        if user_id in contact_data and 'temp_product' in contact_data[user_id]:
            del contact_data[user_id]['temp_product']
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("🛍️ Kategoriyalar"),
            KeyboardButton("🔍 Qidiruv"),
            KeyboardButton("🛒 Savat"),
            KeyboardButton("🌐 Til"),
            KeyboardButton("📋 Buyurtmalar"),
            KeyboardButton("📞 Aloqa")
        )
        
        bot.reply_to(message, "🔙 Orqaga qaytdingiz!", reply_markup=markup)
        return
    
    try:
        quantity = int(message.text)
        if quantity <= 0:
            bot.reply_to(message, "❌ Miqdor 0 dan katta bo'lishi kerak!")
            return
        if quantity > 100:
            bot.reply_to(message, "❌ Bir martada 100 tadan ko'p mahsulot qo'sha olmaysiz!")
            return
        
        # Mahsulot mavjudligini tekshirish
        temp_product = contact_data[user_id]['temp_product']
        product = temp_product['product']
        available_quantity = product.get('quantity', 0)
        
        if quantity > available_quantity:
            bot.reply_to(message, f"❌ Kechirasiz! Bu mahsulotdan faqat {available_quantity} ta mavjud.\n\n"
                                 f"Iltimos, {available_quantity} tadan kamroq son kiriting.")
            return
            
    except ValueError:
        bot.reply_to(message, "❌ Noto'g'ri miqdor! Iltimos, raqam kiriting.")
        return
    
    # Mahsulotni miqdori bilan saqlash
    temp_product = contact_data[user_id]['temp_product']
    product = temp_product['product'].copy()
    product['quantity'] = quantity
    
    # Parametr narxini hisoblash
    param_price = temp_product.get('param_price', 0)
    total_unit_price = product['price'] + param_price
    product['total_price'] = total_unit_price * quantity
    product['unit_price'] = total_unit_price
    product['param_price'] = param_price
    
    # Tanlangan parametrni saqlash
    if 'selected_param' in temp_product:
        product['selected_param'] = temp_product['selected_param']
    
    user_data[user_id]['cart'].append(product)
    
    # Vaqtinchalik ma'lumotlarni tozalash
    if user_id in user_states:
        del user_states[user_id]
    if user_id in contact_data and 'temp_product' in contact_data[user_id]:
        del contact_data[user_id]['temp_product']
    
    # Asosiy menyuga qaytish
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🛍️ Kategoriyalar"),
        KeyboardButton("🔍 Qidiruv"),
        KeyboardButton("🛒 Savat"),
        KeyboardButton("🌐 Til"),
        KeyboardButton("📋 Buyurtmalar"),
        KeyboardButton("📞 Aloqa")
    )
    
    bot.reply_to(message, 
                 f"✅ {product['name']} ({quantity} ta) savatga qo'shildi!\n\n"
                 f"🛒 Savatingizda {len(user_data[user_id]['cart'])} ta mahsulot bor.",
                 reply_markup=create_main_menu(user_id))

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_question")
def handle_question_input(message):
    """Savolni qabul qilish va adminga yuborish"""
    user_id = message.from_user.id
    question = message.text
    
    if user_id not in contact_data:
        contact_data[user_id] = {}
    
    contact_data[user_id]['question'] = question
    contact_data[user_id]['user_id'] = user_id
    contact_data[user_id]['username'] = message.from_user.username or "Noma'lum"
    contact_data[user_id]['first_name'] = message.from_user.first_name or "Noma'lum"
    
    # Username yoki ismni aniqlash
    username_display = ""
    if message.from_user.username:
        username_display = f"@{message.from_user.username}"
    else:
        username_display = message.from_user.first_name or "Noma'lum"
    
    # Adminga xabar yuborish
    admin_message = f"""
📞 Yangi aloqa so'rovi!

👤 Foydalanuvchi: {username_display}
📱 Telefon: +{contact_data[user_id]['phone']}
❓ Savol: {question}
    """
    
    try:
        # Admin uchun javob berish tugmasi bilan xabar
        admin_markup = InlineKeyboardMarkup()
        admin_markup.add(InlineKeyboardButton("💬 Foydalanuvchiga javob berish", callback_data=f"reply_to_user_{user_id}"))
        
        bot.send_message(ADMIN_ID, admin_message, reply_markup=admin_markup)
        
        # Foydalanuvchiga tasdiq
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("🛍️ Kategoriyalar"),
            KeyboardButton("🔍 Qidiruv"),
            KeyboardButton("🛒 Savat"),
            KeyboardButton("🌐 Til"),
            KeyboardButton("📋 Buyurtmalar"),
            KeyboardButton("📞 Aloqa")
        )
        
        bot.reply_to(message, 
                     "✅ Savolingiz muvaffaqiyatli yuborildi!\n\n"
                     "📞 Operatorlar tez orada siz bilan bog'lanishadi.",
                     reply_markup=create_main_menu(user_id))
        
        # Foydalanuvchi holatini tozalash
        if user_id in user_states:
            del user_states[user_id]
        if user_id in contact_data:
            del contact_data[user_id]
            
    except Exception as e:
        bot.reply_to(message, 
                     "❌ Xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.")
        print(f"Admin xabar yuborishda xatolik: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('category_'))
def handle_category_selection(call):
    """Kategoriya tanlash"""
    category = call.data.split('_')[1]
    
    # Kategoriya ma'lumotlarini olish
    category_info = get_category_info(category)
    
    if not category_info:
        bot.answer_callback_query(call.id, "❌ Kategoriya topilmadi!")
        return
    
    # Agar ichki kategoriyalar mavjud bo'lsa
    if 'subcategories' in category_info:
        # Ichki kategoriyalar menyusini ko'rsatish
        bot.edit_message_text(
            f"📂 {category_info['name']} kategoriyasi\n\n"
            f"Ichki kategoriyani tanlang:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=create_subcategory_menu(category)
        )
    else:
        # To'g'ridan-to'g'ri mahsulotlar mavjud
        # Mahsulotlarni yangilash
        update_products()
        
        if category in products and products[category]:
            category_products = products[category]
            markup = InlineKeyboardMarkup(row_width=1)
            
            for product in category_products:
                available_qty = product.get('quantity', 0)
                markup.add(InlineKeyboardButton(
                    f"📦 {product['name']} - {product['price']:,} so'm ({available_qty} ta)",
                    callback_data=f"product_{category}_{category_products.index(product)}"
                ))
            
            markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_categories"))
            
            bot.edit_message_text(
                f"{category_info['name']} mahsulotlari:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup
            )
        else:
            # Agar kategoriyada mahsulot yo'q bo'lsa
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_categories"))
            
            bot.edit_message_text(
                "❌ Bu kategoriyada mahsulotlar yo'q!",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup
            )

@bot.callback_query_handler(func=lambda call: call.data.startswith('subcategory_'))
def handle_subcategory_selection(call):
    """Ichki kategoriya tanlash"""
    parts = call.data.split('_')
    category = parts[1]
    subcategory = parts[2]
    
    # Mahsulotlarni yangilash
    update_products()
    
    # Ichki kategoriya mahsulotlarini olish
    full_key = f"{category}_{subcategory}"
    
    if full_key in products and products[full_key]:
        category_products = products[full_key]
        markup = InlineKeyboardMarkup(row_width=1)
        
        for product in category_products:
            available_qty = product.get('quantity', 0)
            markup.add(InlineKeyboardButton(
                f"📦 {product['name']} - {product['price']:,} so'm ({available_qty} ta)",
                callback_data=f"product_{full_key}_{category_products.index(product)}"
            ))
        
        markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data=f"category_{category}"))
        
        # Ichki kategoriya ma'lumotlarini olish
        subcategory_info = get_category_info(category, subcategory)
        display_name = subcategory_info['name'] if subcategory_info else subcategory.capitalize()
        
        bot.edit_message_text(
            f"{display_name} mahsulotlari:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    else:
        # Agar ichki kategoriyada mahsulot yo'q bo'lsa
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data=f"category_{category}"))
        
        bot.edit_message_text(
            "❌ Bu ichki kategoriyada mahsulotlar yo'q!",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('product_'))
def handle_product_selection(call):
    """Mahsulot tanlash"""
    parts = call.data.split('_')
    
    # Ichki kategoriya yoki oddiy kategoriya ekanligini aniqlash
    if len(parts) == 3:
        # Oddiy kategoriya: product_category_index
        category = parts[1]
        product_index = int(parts[2])
    elif len(parts) == 4:
        # Ichki kategoriya: product_category_subcategory_index
        category = f"{parts[1]}_{parts[2]}"
        product_index = int(parts[3])
    else:
        # Xatolik
        bot.answer_callback_query(call.id, "❌ Xatolik: Noto'g'ri format")
        return
    
    if category in products and product_index < len(products[category]):
        product = products[category][product_index]
        
        # Mahsulot ma'lumotlarini ko'rsatish
        product_text = f"""
📦 **{product['name']}**
💰 **Narxi:** {product['price']:,} so'm
📦 **Mavjud:** {product.get('quantity', 0)} ta
📝 **Tavsif:** {product['description']}
        """
        
        # Xarakteristikalar ko'rsatish
        if 'characteristics' in product and product['characteristics']:
            product_text += "\n🔧 **Xarakteristikalar:**\n"
            for char in product['characteristics']:
                product_text += f"• {char['name']}: {char['value']}\n"
        
        # Parametrlar tugmalarini yaratish
        markup = InlineKeyboardMarkup(row_width=2)
        
        # Agar parametrlar mavjud bo'lsa, ularni ko'rsatish
        if 'parameters' in product and product['parameters']:
            product_text += "\n⚙️ **Parametrlar:**\n"
            for i, param in enumerate(product['parameters']):
                param_price = param.get('price', 0)
                if param_price > 0:
                    param_text = f"{param['name']}: {param['value']} (+{param_price:,} so'm)"
                else:
                    param_text = f"{param['name']}: {param['value']}"
                markup.add(InlineKeyboardButton(
                    param_text, 
                    callback_data=f"select_param_{category}_{product_index}_{i}"
                ))
        
        # Asosiy tugmalar
        markup.add(
            InlineKeyboardButton("🛒 Savatga qo'shish", callback_data=f"add_to_cart_{category}_{product_index}"),
            InlineKeyboardButton("🔙 Orqaga", callback_data=f"category_{category}")
        )
        
        bot.edit_message_text(
            product_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    else:
        # Xatolik xabari
        error_text = f"""
❌ **Xatolik!**

Kategoriya: {category}
Indeks: {product_index}
Mavjud kategoriyalar: {list(products.keys())}
        """
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_categories"))
        
        bot.edit_message_text(
            error_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('select_param_'))
def handle_param_selection(call):
    """Parametr tanlash"""
    parts = call.data.split('_')
    
    # Ichki kategoriya yoki oddiy kategoriya ekanligini aniqlash
    if len(parts) == 5:
        # Oddiy kategoriya: select_param_category_index_param_index
        category = parts[2]
        product_index = int(parts[3])
        param_index = int(parts[4])
    elif len(parts) == 6:
        # Ichki kategoriya: select_param_category_subcategory_index_param_index
        category = f"{parts[2]}_{parts[3]}"
        product_index = int(parts[4])
        param_index = int(parts[5])
    else:
        # Xatolik
        bot.answer_callback_query(call.id, "❌ Xatolik: Noto'g'ri format")
        return
    
    if category in products and product_index < len(products[category]):
        product = products[category][product_index]
        
        if 'parameters' in product and param_index < len(product['parameters']):
            selected_param = product['parameters'][param_index]
            
            # Tanlangan parametrni saqlash
            user_id = call.from_user.id
            if user_id not in contact_data:
                contact_data[user_id] = {}
            contact_data[user_id]['selected_param'] = selected_param
            contact_data[user_id]['temp_product'] = {
                'product': product,
                'category': category,
                'product_index': product_index,
                'selected_param': selected_param,
                'param_price': selected_param.get('price', 0)
            }
            
            # Miqdorni so'rash
            user_states[user_id] = "waiting_quantity"
            
            markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            markup.add(KeyboardButton("🔙 Orqaga"))
            
            # Parametr narxini hisoblash
            param_price = selected_param.get('price', 0)
            total_price = product['price'] + param_price
            
            bot.edit_message_text(
                f"📦 **{product['name']}**\n"
                f"⚙️ **Tanlangan parametr:** {selected_param['name']}: {selected_param['value']}\n"
                f"💰 **Asosiy narx:** {product['price']:,} so'm\n"
                f"💰 **Parametr narxi:** {param_price:,} so'm\n"
                f"💰 **Jami narx:** {total_price:,} so'm\n"
                f"📦 **Mavjud:** {product.get('quantity', 0)} ta\n\n"
                f"🔢 Qancha miqdorda qo'shmoqchisiz? (Maksimal: {product.get('quantity', 0)} ta)",
                call.message.chat.id,
                call.message.message_id
            )
            
            bot.send_message(
                call.message.chat.id,
                "🔢 Miqdorni yozing:",
                reply_markup=markup
            )
        else:
            bot.answer_callback_query(call.id, "❌ Parametr topilmadi!")
    else:
        bot.answer_callback_query(call.id, "❌ Mahsulot topilmadi!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_cart_'))
def handle_add_to_cart(call):
    """Savatga qo'shish - miqdorni so'rash"""
    parts = call.data.split('_')
    
    # Ichki kategoriya yoki oddiy kategoriya ekanligini aniqlash
    if len(parts) == 5:
        # Oddiy kategoriya: add_to_cart_category_index
        category = parts[3]
        product_index = int(parts[4])
    elif len(parts) == 6:
        # Ichki kategoriya: add_to_cart_category_subcategory_index
        category = f"{parts[3]}_{parts[4]}"
        product_index = int(parts[5])
    else:
        # Xatolik
        bot.answer_callback_query(call.id, "❌ Xatolik: Noto'g'ri format")
        return
    
    user_id = call.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {'cart': [], 'language': 'uz', 'orders': []}
    
    if category in products and product_index < len(products[category]):
        product = products[category][product_index]
        
        # Miqdorni so'rash uchun ma'lumotlarni saqlash
        user_states[user_id] = "waiting_quantity"
        if user_id not in contact_data:
            contact_data[user_id] = {}
        contact_data[user_id]['temp_product'] = {
            'product': product,
            'category': category,
            'product_index': product_index,
            'selected_param': None,
            'param_price': 0
        }
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add(KeyboardButton("🔙 Orqaga"))
        
        bot.edit_message_text(
            f"📦 {product['name']}\n"
            f"💰 Narxi: {product['price']:,} so'm\n"
            f"📦 Mavjud: {product.get('quantity', 0)} ta\n\n"
            f"🔢 Qancha miqdorda qo'shmoqchisiz? (Maksimal: {product.get('quantity', 0)} ta)",
            call.message.chat.id,
            call.message.message_id
        )
        
        bot.send_message(
            call.message.chat.id,
            "🔢 Miqdorni yozing:",
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data == "checkout")
def handle_checkout(call):
    """Buyurtma berish - ism va familiyani so'rash"""
    user_id = call.from_user.id
    cart = user_data[user_id]['cart']
    
    if not cart:
        bot.answer_callback_query(call.id, "Savat bo'sh!")
        return
    
    # Buyurtma ma'lumotlarini saqlash uchun
    if user_id not in contact_data:
        contact_data[user_id] = {}
    contact_data[user_id]['checkout_data'] = {}
    user_states[user_id] = "waiting_name"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("🔙 Bekor qilish"))
    
    bot.edit_message_text(
        "📝 Buyurtma berish uchun ma'lumotlaringizni kiriting:\n\n"
        "👤 Ism va familiyangizni yozing:",
        call.message.chat.id,
        call.message.message_id
    )
    
    bot.send_message(
        call.message.chat.id,
        "👤 Ism va familiyangizni yozing:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "clear_cart")
def handle_clear_cart(call):
    """Savatni tozalash"""
    user_id = call.from_user.id
    user_data[user_id]['cart'] = []
    
    bot.edit_message_text(
        "🗑️ Savat tozalandi!",
        call.message.chat.id,
        call.message.message_id
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def handle_language_selection(call):
    """Til tanlash"""
    lang = call.data.split('_')[1]
    user_id = call.from_user.id
    
    if user_id not in user_data:
        user_data[user_id] = {'cart': [], 'language': 'uz', 'orders': []}
    
    # Foydalanuvchi ma'lumotlarini saqlash
    if user_id not in user_data:
        user_data[user_id] = {'cart': [], 'language': 'uz', 'orders': []}
    
    user_data[user_id]['language'] = lang
    
    # data.json ga ham saqlash
    user_found = False
    for user in data['users']:
        if user.get('id') == user_id:
            user['language'] = lang
            user_found = True
            break
    
    if not user_found:
        data['users'].append({
            'id': user_id,
            'language': lang,
            'joined_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    save_data(data)
    
    # Debug uchun print
    print(f"Til o'zgartirildi: User ID: {user_id}, Yangi til: {lang}")
    print(f"user_data[{user_id}]: {user_data[user_id]}")
    print(f"Barcha user_data: {user_data}")
    
    # Til nomlari
    lang_names = {
        'uz': 'O\'zbekcha', 
        'ru': 'Русский', 
        'en': 'English'
    }
    
    # Xabar matnlari
    messages = {
        'uz': {
            'success': f"✅ Til {lang_names[lang]} ga o'zgartirildi!",
            'welcome': "🏠 Asosiy menyuga qaytdingiz!"
        },
        'ru': {
            'success': f"✅ Язык изменен на {lang_names[lang]}!",
            'welcome': "🏠 Вернулись в главное меню!"
        },
        'en': {
            'success': f"✅ Language changed to {lang_names[lang]}!",
            'welcome': "🏠 Returned to main menu!"
        }
    }
    
    # Foydalanuvchi tiliga qarab xabar yuborish
    user_lang = user_data[user_id]['language']
    msg = messages[user_lang]
    
    # Til o'zgartirildi xabari
    bot.answer_callback_query(call.id, msg['success'])
    
    # Asosiy menyuga qaytish - yangi xabar yuborish
    bot.send_message(
        call.message.chat.id,
        f"{msg['success']}\n\n{msg['welcome']}",
        reply_markup=create_main_menu(user_id)
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_categories")
def handle_back_to_categories(call):
    """Kategoriyalarga qaytish"""
    bot.edit_message_text(
        "Mahsulot kategoriyalarini tanlang:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=create_category_menu()
    )

@bot.callback_query_handler(func=lambda call: call.data == "no_products")
def handle_no_products(call):
    """Mahsulotlar yo'q bo'lganda"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_to_main"))
    
    bot.edit_message_text(
        "❌ Hozirda mahsulotlar yo'q!\n\n"
        "Iltimos, keyinroq qayta urinib ko'ring yoki admin bilan bog'laning.",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def handle_back_to_main(call):
    """Asosiy menyuga qaytish"""
    user_id = call.from_user.id
    
    # Admin uchun maxsus menyu
    if user_id == ADMIN_ID:
        welcome_text = """
🎉 Xush kelibsiz! Online do'kon botiga!

Quyidagi tugmalardan birini tanlang:
🛍️ Kategoriyalar - mahsulotlarni ko'rish
🔍 Qidiruv - mahsulotlarni qidirish
🛒 Savat - tanlangan mahsulotlar
🌐 Til - tilni o'zgartirish
📋 Buyurtmalar - buyurtmalar tarixi
📞 Aloqa - operator bilan bog'lanish
🔧 Admin Panel - bot boshqaruvi
        """
        
        # Admin uchun maxsus markup
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🛍️ Kategoriyalar", callback_data="show_categories"),
            InlineKeyboardButton("🔍 Qidiruv", callback_data="start_search"),
            InlineKeyboardButton("🛒 Savat", callback_data="show_cart"),
            InlineKeyboardButton("🌐 Til", callback_data="show_languages"),
            InlineKeyboardButton("📋 Buyurtmalar", callback_data="show_orders"),
            InlineKeyboardButton("📞 Aloqa", callback_data="start_contact"),
            InlineKeyboardButton("🔧 Admin Panel", callback_data="go_to_admin_panel")
        )
        
        bot.edit_message_text(welcome_text, call.message.chat.id, call.message.message_id, reply_markup=markup)
    else:
        welcome_text = """
🎉 Xush kelibsiz! Online do'kon botiga!

Quyidagi tugmalardan birini tanlang:
🛍️ Kategoriyalar - mahsulotlarni ko'rish
🔍 Qidiruv - mahsulotlarni qidirish
🛒 Savat - tanlangan mahsulotlar
🌐 Til - tilni o'zgartirish
📋 Buyurtmalar - buyurtmalar tarixi
📞 Aloqa - operator bilan bog'lanish
        """
        
        # Oddiy foydalanuvchi uchun markup
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🛍️ Kategoriyalar", callback_data="show_categories"),
            InlineKeyboardButton("🔍 Qidiruv", callback_data="start_search"),
            InlineKeyboardButton("🛒 Savat", callback_data="show_cart"),
            InlineKeyboardButton("🌐 Til", callback_data="show_languages"),
            InlineKeyboardButton("📋 Buyurtmalar", callback_data="show_orders"),
            InlineKeyboardButton("📞 Aloqa", callback_data="start_contact")
        )
        
        bot.edit_message_text(welcome_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('search_product_'))
def handle_search_product_selection(call):
    """Qidiruv natijasidan mahsulot tanlash"""
    parts = call.data.split('_')
    category = parts[2]
    product_index = int(parts[3])
    
    if category in products and product_index < len(products[category]):
        product = products[category][product_index]
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🛒 Savatga qo'shish", callback_data=f"add_to_cart_{category}_{product_index}"),
            InlineKeyboardButton("🔙 Qidiruv natijalariga qaytish", callback_data="back_to_search_results")
        )
        
        product_text = f"""
📦 {product['name']}
💰 Narxi: {product['price']:,} so'm
📝 {product['description']}
🏷️ Kategoriya: {category.capitalize()}
        """
        
        bot.edit_message_text(
            product_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data == "search_again")
def handle_search_again(call):
    """Qayta qidiruv"""
    user_id = call.from_user.id
    user_states[user_id] = "searching"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("🔙 Asosiy menyu"))
    
    bot.edit_message_text(
        "🔍 Qanday mahsulot qidirayapsiz?\n\n"
        "Mahsulot nomini yoki kalit so'zlarni yozing (masalan: iPhone, kurtka, kitob)",
        call.message.chat.id,
        call.message.message_id
    )
    
    bot.send_message(
        call.message.chat.id,
        "🔍 Yangi qidiruvni boshlang:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_search_results")
def handle_back_to_search_results(call):
    """Qidiruv natijalariga qaytish"""
    bot.answer_callback_query(call.id, "Qidiruv natijalariga qaytish uchun qayta qidiruv qiling.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('payment_'))
def handle_payment_method(call):
    """Tolov usulini qabul qilish"""
    user_id = call.from_user.id
    payment_method = call.data.split('_')[1]
    
    if user_id not in contact_data or 'checkout_data' not in contact_data[user_id]:
        bot.answer_callback_query(call.id, "Xatolik! Qaytadan urinib ko'ring.")
        return
    
    checkout_data = contact_data[user_id]['checkout_data']
    cart = user_data[user_id]['cart']
    
    # Buyurtma ma'lumotlarini tayyorlash
    total = sum(item.get('total_price', item['price'] * item.get('quantity', 1)) for item in cart)
    items = []
    for item in cart:
        quantity = item.get('quantity', 1)
        items.append(f"{item['name']} ({quantity} ta)")
    
    if payment_method == "card":
        # Karta bilan to'lov
        # Buyurtma ma'lumotlarini saqlash
        contact_data[user_id]['pending_order'] = {
            'total': total,
            'items': items,
            'customer_name': checkout_data['name'],
            'customer_phone': checkout_data['phone'],
            'customer_address': checkout_data['address'],
            'cart_items': cart.copy()
        }
        
        # Karta raqamini yuborish
        card_message = f"""
💳 Karta bilan to'lov

💰 To'lov miqdori: {total:,} so'm
📦 Mahsulotlar: {', '.join(items)}

💳 To'lov qilish uchun quyidagi karta raqamga o'tkazma qiling:

🏦 **Karta raqam:** {data['settings']['payment_card']}
�� **Mulkdor:** {data['settings']['payment_owner']}
🏛️ **Bank:** {data['settings']['payment_bank']}

📸 To'lov chekini skrinshot qilib yuboring!
        """
        
        # Foydalanuvchi holatini o'zgartirish
        user_states[user_id] = "waiting_payment_screenshot"
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        markup.add(KeyboardButton("📍 Lokatsiyani yuboring", request_location=True))
        markup.add(KeyboardButton("🔙 Bekor qilish"))
        
        bot.edit_message_text(
            card_message,
            call.message.chat.id,
            call.message.message_id
        )
        
        bot.send_message(
            call.message.chat.id,
            "📸 To'lov chekini skrinshot qilib yuboring:",
            reply_markup=markup
        )
    
    elif payment_method == "cash":
        # Naqd pul to'lovi
        
        # Mahsulot miqdorlarini kamaytirish va tugaganlarni o'chirish
        cart_items = user_data[user_id]['cart']
        for item in cart_items:
            category = None
            product_index = None
            
            # Mahsulotni topish
            for cat_name, cat_products in products.items():
                for i, product in enumerate(cat_products):
                    if product['name'] == item['name']:
                        category = cat_name
                        product_index = i
                        break
                if category:
                    break
            
            if category and product_index is not None:
                # Mahsulot miqdorini kamaytirish
                current_quantity = products[category][product_index]['quantity']
                ordered_quantity = item.get('quantity', 1)
                new_quantity = current_quantity - ordered_quantity
                
                if new_quantity <= 0:
                    # Mahsulot tugadi - avtomatik o'chirish
                    # data.json dan ham o'chirish
                    for cat_key, cat_data in data['categories'].items():
                        for idx, prod in enumerate(cat_data['products']):
                            if prod['name'] == item['name']:
                                del data['categories'][cat_key]['products'][idx]
                                print(f"Mahsulot avtomatik o'chirildi: {item['name']}")
                                break
                        else:
                            continue
                        break
                    
                    # products global dictionary dan ham o'chirish
                    if category in products and product_index < len(products[category]):
                        del products[category][product_index]
                        print(f"Mahsulot global dictionary dan o'chirildi: {item['name']}")
                    
                    # Admin ga mahsulot tugagani haqida xabar yuborish
                    admin_out_of_stock_message = f"""
⚠️ **Mahsulot tugadi va avtomatik o'chirildi!**

📦 **Mahsulot:** {item['name']}
💰 **Narxi:** {item['price']:,} so'm
📊 **Sotilgan miqdor:** {ordered_quantity} ta
🏷️ **Kategoriya:** {category}

🔄 Mahsulot avtomatik ravishda o'chirildi va foydalanuvchilar ko'ra olmaydi.
                    """
                    bot.send_message(ADMIN_ID, admin_out_of_stock_message)
                else:
                    # Mahsulot miqdorini yangilash
                    products[category][product_index]['quantity'] = new_quantity
                    # data.json da ham yangilash
                    for cat_key, cat_data in data['categories'].items():
                        for prod in cat_data['products']:
                            if prod['name'] == item['name']:
                                prod['quantity'] = new_quantity
                                break
                    print(f"Mahsulot miqdori yangilandi: {item['name']} - {new_quantity} ta")
        
        # Buyurtmani saqlash
        order = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'total': total,
            'items': items,
            'customer_name': checkout_data['name'],
            'customer_phone': checkout_data['phone'],
            'customer_address': checkout_data['address'],
            'payment_method': payment_method,
            'status': 'pending'
        }
        user_data[user_id]['orders'].append(order)
        
        # data.json ga ham saqlash
        data['orders'].append(order)
        save_data(data)
        
        # Products dictionary ni yangilash
        update_products()
        
        # Savatni tozalash
        user_data[user_id]['cart'] = []
        
        # Admin ga barcha ma'lumotlarni yuborish
        admin_detailed_message = f"""
✅ **Yangi naqd pul buyurtmasi qabul qilindi!**

👤 **Mijoz ma'lumotlari:**
• Ism: {checkout_data['name']}
• Telefon: {checkout_data['phone']}
• Manzil: {checkout_data['address']}

💰 **To'lov ma'lumotlari:**
• To'lov usuli: Naqd pul
• Jami summa: {total:,} so'm

📦 **Buyurtma mahsulotlari:**
{chr(10).join([f"• {item['name']} - {item.get('quantity', 1)} ta - {item['price']:,} so'm" for item in cart_items])}

📊 **Mahsulot miqdori o'zgarishlari:**
"""
        
        # Mahsulot miqdori o'zgarishlarini qo'shish
        for item in cart_items:
            category = None
            product_index = None
            
            # Mahsulotni topish
            for cat_name, cat_products in products.items():
                for i, product in enumerate(cat_products):
                    if product['name'] == item['name']:
                        category = cat_name
                        product_index = i
                        break
                if category:
                    break
            
            if category and product_index is not None:
                ordered_quantity = item.get('quantity', 1)
                admin_detailed_message += f"• {item['name']}: {ordered_quantity} ta sotildi\n"
            else:
                admin_detailed_message += f"• {item['name']}: Mahsulot topilmadi (o'chirilgan)\n"
        
        # Admin ga yuborish
        bot.send_message(ADMIN_ID, admin_detailed_message)
        
        success_message = f"""
✅ Buyurtmangiz qabul qilindi!

👤 Mijoz: {checkout_data['name']}
📱 Telefon: {checkout_data['phone']}
📍 Manzil: {checkout_data['address']}
💵 Tolov: Naqd pul
📦 Mahsulotlar: {', '.join(items)}
💰 Jami: {total:,} so'm

📞 Operatorlar tez orada siz bilan bog'lanishadi!
        """
        
        # Asosiy menyuga qaytish
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("🛍️ Kategoriyalar"),
            KeyboardButton("🔍 Qidiruv"),
            KeyboardButton("🛒 Savat"),
            KeyboardButton("🌐 Til"),
            KeyboardButton("📋 Buyurtmalar"),
            KeyboardButton("📞 Aloqa")
        )
        
        bot.edit_message_text(
            success_message,
            call.message.chat.id,
            call.message.message_id
        )
        
        # Asosiy menyuni yuborish
        bot.send_message(
            call.message.chat.id,
            "🏠 Asosiy menyuga qaytdingiz!",
            reply_markup=create_main_menu(user_id)
        )
        
        # Foydalanuvchi holatini tozalash
        if user_id in user_states:
            del user_states[user_id]
        if user_id in contact_data and 'checkout_data' in contact_data[user_id]:
            del contact_data[user_id]['checkout_data']

@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_payment_'))
def handle_approve_payment(call):
    """To'lovni tasdiqlash"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Siz admin emassiz!")
        return
    
    user_id = int(call.data.split('_')[2])
    
    if user_id not in contact_data or 'pending_order' not in contact_data[user_id]:
        bot.answer_callback_query(call.id, "Buyurtma topilmadi!")
        return
    
    pending_order = contact_data[user_id]['pending_order']
    cart_items = pending_order['cart_items']
    
    # Mahsulot miqdorlarini kamaytirish
    for item in cart_items:
        category = None
        product_index = None
        
        # Mahsulotni topish
        for cat_name, cat_products in products.items():
            for i, product in enumerate(cat_products):
                if product['name'] == item['name']:
                    category = cat_name
                    product_index = i
                    break
            if category:
                break
        
        if category and product_index is not None:
            # Mahsulot miqdorini kamaytirish
            current_quantity = products[category][product_index]['quantity']
            ordered_quantity = item.get('quantity', 1)
            new_quantity = current_quantity - ordered_quantity
            
            if new_quantity <= 0:
                # Mahsulot tugadi - avtomatik o'chirish
                # data.json dan ham o'chirish
                for cat_key, cat_data in data['categories'].items():
                    for idx, prod in enumerate(cat_data['products']):
                        if prod['name'] == item['name']:
                            del data['categories'][cat_key]['products'][idx]
                            print(f"Mahsulot avtomatik o'chirildi: {item['name']}")
                            break
                    else:
                        continue
                    break
                
                # products global dictionary dan ham o'chirish
                if category in products and product_index < len(products[category]):
                    del products[category][product_index]
                    print(f"Mahsulot global dictionary dan o'chirildi: {item['name']}")
                
                # Admin ga mahsulot tugagani haqida xabar yuborish
                admin_out_of_stock_message = f"""
⚠️ **Mahsulot tugadi va avtomatik o'chirildi!**

📦 **Mahsulot:** {item['name']}
💰 **Narxi:** {item['price']:,} so'm
📊 **Sotilgan miqdor:** {ordered_quantity} ta
🏷️ **Kategoriya:** {category}

🔄 Mahsulot avtomatik ravishda o'chirildi va foydalanuvchilar ko'ra olmaydi.
                """
                bot.send_message(ADMIN_ID, admin_out_of_stock_message)
            else:
                # Mahsulot miqdorini yangilash
                products[category][product_index]['quantity'] = new_quantity
                # data.json da ham yangilash
                for cat_key, cat_data in data['categories'].items():
                    for prod in cat_data['products']:
                        if prod['name'] == item['name']:
                            prod['quantity'] = new_quantity
                            break
                print(f"Mahsulot miqdori yangilandi: {item['name']} - {new_quantity} ta")
    
    # Buyurtmani saqlash
    order = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'total': pending_order['total'],
        'items': pending_order['items'],
        'customer_name': pending_order['customer_name'],
        'customer_phone': pending_order['customer_phone'],
        'customer_address': pending_order['customer_address'],
        'payment_method': 'card_approved',
        'status': 'approved'
    }
    
    if user_id not in user_data:
        user_data[user_id] = {'cart': [], 'language': 'uz', 'orders': []}
    user_data[user_id]['orders'].append(order)
    
    # data.json ga ham saqlash
    data['orders'].append(order)
    save_data(data)
    
    # Products dictionary ni yangilash
    update_products()
    
    # Savatni tozalash
    user_data[user_id]['cart'] = []
    
    # Admin ga barcha ma'lumotlarni yuborish
    admin_detailed_message = f"""
✅ **To'lov tasdiqlandi va buyurtma qabul qilindi!**

👤 **Mijoz ma'lumotlari:**
• Ism: {pending_order['customer_name']}
• Telefon: {pending_order['customer_phone']}
• Manzil: {pending_order['customer_address']}

💰 **To'lov ma'lumotlari:**
• To'lov usuli: Karta (tasdiqlangan)
• Jami summa: {pending_order['total']:,} so'm

📦 **Buyurtma mahsulotlari:**
{chr(10).join([f"• {item['name']} - {item.get('quantity', 1)} ta - {item['price']:,} so'm" for item in cart_items])}

📊 **Mahsulot miqdori o'zgarishlari:**
"""
    
    # Mahsulot miqdori o'zgarishlarini qo'shish
    for item in cart_items:
        category = None
        product_index = None
        
        # Mahsulotni topish
        for cat_name, cat_products in products.items():
            for i, product in enumerate(cat_products):
                if product['name'] == item['name']:
                    category = cat_name
                    product_index = i
                    break
            if category:
                break
        
        if category and product_index is not None:
            ordered_quantity = item.get('quantity', 1)
            admin_detailed_message += f"• {item['name']}: {ordered_quantity} ta sotildi\n"
        else:
            admin_detailed_message += f"• {item['name']}: Mahsulot topilmadi (o'chirilgan)\n"
    
    # Admin ga yuborish
    bot.send_message(ADMIN_ID, admin_detailed_message)
    
    # Foydalanuvchiga muvaffaqiyatli xabar
    success_message = f"""
✅ To'lov tasdiqlandi!

👤 Mijoz: {pending_order['customer_name']}
📱 Telefon: {pending_order['customer_phone']}
💳 Tolov: Karta (tasdiqlangan)
📦 Mahsulotlar: {', '.join(pending_order['items'])}
💰 Jami: {pending_order['total']:,} so'm

📦 Mahsulotlaringiz tez orada yetkazib beriladi!
    """
    
    # Asosiy menyuga qaytish
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🛍️ Kategoriyalar"),
        KeyboardButton("🔍 Qidiruv"),
        KeyboardButton("🛒 Savat"),
        KeyboardButton("🌐 Til"),
        KeyboardButton("📋 Buyurtmalar"),
        KeyboardButton("📞 Aloqa")
    )
    
    try:
        bot.send_message(user_id, success_message)
        bot.send_message(user_id, "🏠 Asosiy menyuga qaytdingiz!", reply_markup=create_main_menu(user_id))
        
        # Lokatsiyani alohida yuborish
        print(f"Pending order keys: {pending_order.keys()}")
        if 'location' in pending_order:
            print(f"Location found: {pending_order['location']}")
            try:
                bot.send_location(
                    user_id,
                    latitude=pending_order['location']['latitude'],
                    longitude=pending_order['location']['longitude']
                )
                print("Location sent to user successfully")
            except Exception as e:
                print(f"Error sending location to user: {e}")
        else:
            print("Location not found in pending_order")
        
        # Admin ga tasdiq
        bot.edit_message_caption(
            f"✅ To'lov tasdiqlandi!\n\n{call.message.caption}",
            call.message.chat.id,
            call.message.message_id
        )
        
        # Foydalanuvchi holatini tozalash
        if user_id in user_states:
            del user_states[user_id]
        if user_id in contact_data and 'pending_order' in contact_data[user_id]:
            del contact_data[user_id]['pending_order']
            
    except Exception as e:
        bot.answer_callback_query(call.id, f"Xatolik: {e}")
        print(f"To'lov tasdiqlashda xatolik: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_payment_'))
def handle_reject_payment(call):
    """To'lovni rad etish"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Siz admin emassiz!")
        return
    
    user_id = int(call.data.split('_')[2])
    
    if user_id not in contact_data or 'pending_order' not in contact_data[user_id]:
        bot.answer_callback_query(call.id, "Buyurtma topilmadi!")
        return
    
    # Foydalanuvchiga rad etish xabari
    reject_message = f"""
❌ To'lov rad etildi!

💳 To'lov cheki noto'g'ri yoki to'liq emas.
📞 Qo'shimcha ma'lumot uchun "📞 Aloqa" tugmasini bosing.
    """
    
    # Asosiy menyuga qaytish
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🛍️ Kategoriyalar"),
        KeyboardButton("🔍 Qidiruv"),
        KeyboardButton("🛒 Savat"),
        KeyboardButton("🌐 Til"),
        KeyboardButton("📋 Buyurtmalar"),
        KeyboardButton("📞 Aloqa")
    )
    
    try:
        bot.send_message(user_id, reject_message, reply_markup=create_main_menu(user_id))
        
        # Admin ga tasdiq
        bot.edit_message_caption(
            f"❌ To'lov rad etildi!\n\n{call.message.caption}",
            call.message.chat.id,
            call.message.message_id
        )
        
        # Foydalanuvchi holatini tozalash
        if user_id in user_states:
            del user_states[user_id]
        if user_id in contact_data and 'pending_order' in contact_data[user_id]:
            del contact_data[user_id]['pending_order']
            
    except Exception as e:
        bot.answer_callback_query(call.id, f"Xatolik: {e}")
        print(f"To'lov rad etishda xatolik: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_to_user_'))
def handle_admin_reply_request(call):
    """Admin javob berishni boshlash"""
    # Faqat admin javob bera oladi
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Siz admin emassiz!")
        return
    
    user_id = int(call.data.split('_')[3])
    admin_reply_data[call.from_user.id] = {'target_user_id': user_id}
    user_states[call.from_user.id] = "admin_reply"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.edit_message_text(
        f"💬 Foydalanuvchi ID: {user_id} ga javob yozing:\n\n"
        "Javobingizni yozing yoki 'Bekor qilish' tugmasini bosing:",
        call.message.chat.id,
        call.message.message_id
    )
    
    bot.send_message(
        call.message.chat.id,
        "📝 Javobingizni yozing:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_reply")
def handle_admin_reply_message(message):
    """Admin javobini qabul qilish va foydalanuvchiga yuborish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Bekor qilish":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in admin_reply_data:
            del admin_reply_data[message.from_user.id]
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("🛍️ Kategoriyalar"),
            KeyboardButton("🔍 Qidiruv"),
            KeyboardButton("🛒 Savat"),
            KeyboardButton("🌐 Til"),
            KeyboardButton("📋 Buyurtmalar"),
            KeyboardButton("📞 Aloqa")
        )
        
        bot.reply_to(message, "❌ Javob berish bekor qilindi.", reply_markup=markup)
        return
    
    # Javobni foydalanuvchiga yuborish
    target_user_id = admin_reply_data[message.from_user.id]['target_user_id']
    admin_reply = message.text
    
    # Foydalanuvchi ismini aniqlash
    try:
        user_info = bot.get_chat(target_user_id)
        user_name = user_info.first_name or user_info.username or f"User {target_user_id}"
    except:
        user_name = f"User {target_user_id}"
    
    try:
        # Foydalanuvchiga javob yuborish
        user_message = f"""
📞 Operator javobi:

{admin_reply}

---
Savolingizga javob berildi. Qo'shimcha savollaringiz bo'lsa, "📞 Aloqa" tugmasini bosing.
        """
        
        bot.send_message(target_user_id, user_message, reply_markup=create_main_menu(target_user_id))
        
        # Admin ga tasdiq va asosiy menyuga qaytish
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("🛍️ Kategoriyalar"),
            KeyboardButton("🔍 Qidiruv"),
            KeyboardButton("🛒 Savat"),
            KeyboardButton("🌐 Til"),
            KeyboardButton("📋 Buyurtmalar"),
            KeyboardButton("📞 Aloqa")
        )
        
        bot.reply_to(message, f"✅ Javob foydalanuvchi {user_name} ga yuborildi!", reply_markup=create_main_menu(message.from_user.id))
        
        # Admin holatini tozalash
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in admin_reply_data:
            del admin_reply_data[message.from_user.id]
            
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {e}")
        print(f"Admin javob yuborishda xatolik: {e}")

# Admin callback handlers (eski - endi ishlatilmaydi)
# @bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
# def handle_admin_callbacks(call):
#     """Admin panel callback handlerlari"""
#     if call.from_user.id != ADMIN_ID:
#         bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
#         return
#     
#     action = call.data.split('_')[1]
#     
#     if action == "stats":
#         show_admin_stats(call)
#     elif action == "products":
#         show_admin_products(call)
#     elif action == "categories":
#         show_admin_categories(call)
#     elif action == "orders":
#         show_admin_orders(call)
#     elif action == "users":
#         show_admin_users(call)
#     elif action == "settings":
#         show_admin_settings(call)

def show_admin_stats(call):
    """Admin statistikasini ko'rsatish"""
    total_users = len(data['users'])
    total_orders = len(data['orders'])
    total_products = sum(len(cat['products']) for cat in data['categories'].values())
    total_categories = len(data['categories'])
    
    # Bugungi buyurtmalar
    today = datetime.now().strftime("%Y-%m-%d")
    today_orders = [order for order in data['orders'] if order['date'].startswith(today)]
    
    stats_text = f"""
📊 **Bot Statistikasi**

👥 **Foydalanuvchilar:**
• Jami: {total_users} ta
• Bugun faol: {len(today_orders)} ta

📦 **Mahsulotlar:**
• Kategoriyalar: {total_categories} ta
• Mahsulotlar: {total_products} ta

📋 **Buyurtmalar:**
• Jami: {total_orders} ta
• Bugun: {len(today_orders)} ta

💰 **Bugungi tushum:**
• {sum(order.get('total', 0) for order in today_orders):,} so'm
    """
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
    
    bot.edit_message_text(stats_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

def show_admin_products(call):
    """Admin mahsulotlar boshqaruvi"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ Mahsulot qo'shish", callback_data="admin_add_product"),
        InlineKeyboardButton("✏️ Mahsulot tahrirlash", callback_data="admin_edit_product"),
        InlineKeyboardButton("🗑️ Mahsulot o'chirish", callback_data="admin_delete_product"),
        InlineKeyboardButton("📊 Mahsulot statistikasi", callback_data="admin_product_stats")
    )
    markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
    
    products_text = """
📦 **Mahsulotlar Boshqaruvi**

Quyidagi amallardan birini tanlang:
➕ Mahsulot qo'shish - yangi mahsulot qo'shish
✏️ Mahsulot tahrirlash - mavjud mahsulotni o'zgartirish
🗑️ Mahsulot o'chirish - mahsulotni o'chirish
📊 Mahsulot statistikasi - mahsulotlar haqida ma'lumot
    """
    
    bot.edit_message_text(products_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

def show_admin_categories(call):
    """Admin kategoriyalar boshqaruvi"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ Kategoriya qo'shish", callback_data="admin_add_category"),
        InlineKeyboardButton("✏️ Kategoriya tahrirlash", callback_data="admin_edit_category"),
        InlineKeyboardButton("🗑️ Kategoriya o'chirish", callback_data="admin_delete_category")
    )
    markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
    
    categories_text = f"""
🏷️ **Kategoriyalar Boshqaruvi**

Jami kategoriyalar: {len(data['categories'])} ta

Quyidagi amallardan birini tanlang:
➕ Kategoriya qo'shish - yangi kategoriya qo'shish
✏️ Kategoriya tahrirlash - mavjud kategoriyani o'zgartirish
🗑️ Kategoriya o'chirish - kategoriyani o'chirish
    """
    
    bot.edit_message_text(categories_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

def show_admin_orders(call):
    """Admin buyurtmalar boshqaruvi"""
    if not data['orders']:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
        bot.edit_message_text("📋 Hali buyurtmalar yo'q!", call.message.chat.id, call.message.message_id, reply_markup=markup)
        return
    
    # Oxirgi 5 ta buyurtmani ko'rsatish
    recent_orders = data['orders'][-5:]
    
    orders_text = f"""
📋 **Buyurtmalar Boshqaruvi**

Jami buyurtmalar: {len(data['orders'])} ta

**Oxirgi buyurtmalar:**
"""
    
    for i, order in enumerate(reversed(recent_orders), 1):
        orders_text += f"""
{i}. 📦 Buyurtma #{len(data['orders']) - len(recent_orders) + i}
   👤 {order.get('customer_name', 'Noma lum')}
   📱 {order.get('customer_phone', 'Noma lum')}
   💰 {order.get('total', 0):,} so'm
   📅 {order.get('date', 'Noma lum')}
"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📋 Barcha buyurtmalar", callback_data="admin_all_orders"),
        InlineKeyboardButton("🗑️ Buyurtma o'chirish", callback_data="admin_delete_order")
    )
    markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
    
    bot.edit_message_text(orders_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

def show_admin_users(call):
    """Admin foydalanuvchilar boshqaruvi"""
    if not data['users']:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
        bot.edit_message_text("👥 Hali foydalanuvchilar yo'q!", call.message.chat.id, call.message.message_id, reply_markup=markup)
        return
    
    # Oxirgi 5 ta foydalanuvchini ko'rsatish
    recent_users = data['users'][-5:]
    
    users_text = f"""
👥 **Foydalanuvchilar Boshqaruvi**

Jami foydalanuvchilar: {len(data['users'])} ta

**Oxirgi ro'yxatdan o'tganlar:**
"""
    
    for i, user in enumerate(reversed(recent_users), 1):
        username = user.get('username', 'Noma lum')
        first_name = user.get('first_name', 'Noma lum')
        joined_date = user.get('joined_date', 'Noma lum')
        
        users_text += f"""
{i}. 👤 {first_name} (@{username})
   📅 {joined_date}
"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👥 Barcha foydalanuvchilar", callback_data="admin_all_users"),
        InlineKeyboardButton("🗑️ Foydalanuvchi o'chirish", callback_data="admin_delete_user")
    )
    markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
    
    bot.edit_message_text(users_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

def show_admin_settings(call):
    """Admin sozlamalar"""
    settings_text = f"""
⚙️ **Bot Sozlamalari**

🔑 **Bot Token:** {data['settings']['bot_token']}
👤 **Admin ID:** {data['settings']['admin_id']}

💳 **To'lov ma'lumotlari:**
🏦 Karta raqam: {data['settings']['payment_card']}
👤 Mulkdor: {data['settings']['payment_owner']}
🏛️ Bank: {data['settings']['payment_bank']}
    """
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔑 Token o'zgartirish", callback_data="admin_change_token"),
        InlineKeyboardButton("👤 Admin ID o'zgartirish", callback_data="admin_change_admin"),
        InlineKeyboardButton("💳 To'lov ma'lumotlari", callback_data="admin_change_payment")
    )
    markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back"))
    
    bot.edit_message_text(settings_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

# Admin orqaga qaytish
@bot.callback_query_handler(func=lambda call: call.data == "admin_back")
def admin_back(call):
    """Admin panelga qaytish"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    admin_text = """
🔧 **Admin Panel**

Quyidagi funksiyalardan birini tanlang:
📊 Statistika - umumiy ma'lumotlar
📦 Mahsulotlar - mahsulotlarni boshqarish
🏷️ Kategoriyalar - kategoriyalarni boshqarish
📋 Buyurtmalar - buyurtmalarni ko'rish
👥 Foydalanuvchilar - foydalanuvchilar ro'yxati
⚙️ Sozlamalar - bot sozlamalari
    """
    
    bot.edit_message_text(admin_text, call.message.chat.id, call.message.message_id, reply_markup=create_admin_menu())

# Kategoriya qo'shish
@bot.callback_query_handler(func=lambda call: call.data == "admin_add_category")
def admin_add_category_start(call):
    """Kategoriya qo'shishni boshlash"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    user_states[call.from_user.id] = "admin_add_category_name"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.edit_message_text(
        "🏷️ Yangi kategoriya qo'shish\n\n"
        "Kategoriya nomini yozing (masalan: Elektronika):",
        call.message.chat.id, call.message.message_id
    )
    
    bot.send_message(
        call.message.chat.id,
        "📝 Kategoriya nomini yozing:",
        reply_markup=markup
    )

# Mahsulot qo'shish
@bot.callback_query_handler(func=lambda call: call.data == "admin_add_product")
def admin_add_product_start(call):
    """Mahsulot qo'shishni boshlash"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    # Kategoriyalar ro'yxatini ko'rsatish
    markup = InlineKeyboardMarkup(row_width=1)
    
    for category_key, category_data in data['categories'].items():
        emoji = category_data.get('emoji', '📦')
        name = category_data['name']
        markup.add(InlineKeyboardButton(
            f"{emoji} {name}",
            callback_data=f"admin_add_product_to_{category_key}"
        ))
    
    markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_products"))
    
    bot.edit_message_text(
        "📦 Yangi mahsulot qo'shish\n\n"
        "Qaysi kategoriyaga qo'shmoqchisiz?",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup
    )

# Mahsulot qo'shish - kategoriya tanlash
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_add_product_to_"))
def admin_add_product_category_selected(call):
    """Mahsulot qo'shish uchun kategoriya tanlanganda"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    category_key = call.data.split("admin_add_product_to_")[1]
    
    # Foydalanuvchi holatini saqlash
    user_states[call.from_user.id] = "admin_add_product_name"
    if call.from_user.id not in contact_data:
        contact_data[call.from_user.id] = {}
    contact_data[call.from_user.id]['new_product'] = {'category': category_key}
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    category_name = data['categories'][category_key]['name']
    
    bot.edit_message_text(
        f"📦 Yangi mahsulot qo'shish\n\n"
        f"Kategoriya: {category_name}\n\n"
        f"Mahsulot nomini yozing:",
        call.message.chat.id, call.message.message_id
    )
    
    bot.send_message(
        call.message.chat.id,
        "📝 Mahsulot nomini yozing:",
        reply_markup=markup
    )

# Admin xabar handlerlari
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_add_product_category")
def handle_admin_add_product_category(message):
    """Mahsulot qo'shish uchun kategoriya tanlanganda"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Orqaga":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        
        bot.reply_to(message, "❌ Mahsulot qo'shish bekor qilindi.", reply_markup=create_admin_menu())
        return
    
    # Kategoriya nomini topish (to'liq moslik)
    category_key = None
    for key, category_data in data['categories'].items():
        emoji = category_data.get('emoji', '📦')
        name = category_data['name']
        button_text = f"{emoji} {name}"
        
        # Faqat to'liq moslik
        if button_text == message.text:
            category_key = key
            break
    
    if not category_key:
        bot.reply_to(message, "❌ Kategoriya topilmadi! Iltimos, qayta tanlang.")
        return
    
    # Foydalanuvchi holatini saqlash
    user_states[message.from_user.id] = "admin_add_product_name"
    if message.from_user.id not in contact_data:
        contact_data[message.from_user.id] = {}
    contact_data[message.from_user.id]['new_product'] = {'category': category_key}
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("🔙 Orqaga"))
    
    category_name = data['categories'][category_key]['name']
    
    bot.reply_to(message, 
                 f"📦 Yangi mahsulot qo'shish\n\n"
                 f"Kategoriya: {category_name}\n\n"
                 f"Mahsulot nomini yozing:",
                 reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_delete_category")
def handle_admin_delete_category(message):
    """Kategoriya o'chirish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Orqaga":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        
        bot.reply_to(message, "❌ Kategoriya o'chirish bekor qilindi.", reply_markup=create_admin_menu())
        return
    
    # Kategoriya nomini topish
    category_key = None
    for key, category_data in data['categories'].items():
        if category_data['name'] in message.text:
            category_key = key
            break
    
    if not category_key:
        bot.reply_to(message, "❌ Kategoriya topilmadi! Iltimos, qayta tanlang.")
        return
    
    try:
        category_name = data['categories'][category_key]['name']
        product_count = len(data['categories'][category_key]['products'])
        
        # Kategoriyani o'chirish
        del data['categories'][category_key]
        
        # data.json ga saqlash
        save_data(data)
        
        # Mahsulotlarni yangilash
        update_products()
        
        success_text = f"""
✅ Kategoriya muvaffaqiyatli o'chirildi!

🗑️ Kategoriya: {category_name}
🗑️ O'chirilgan mahsulotlar: {product_count} ta
        """
        
        bot.reply_to(message, success_text, reply_markup=create_admin_menu())
        
        # Foydalanuvchi holatini tozalash
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
            
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik yuz berdi: {e}", reply_markup=create_admin_menu())

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_delete_product_category")
def handle_admin_delete_product_category(message):
    """Mahsulot o'chirish uchun kategoriya tanlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Orqaga":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("➕ Mahsulot qo'shish"),
            KeyboardButton("✏️ Mahsulot tahrirlash"),
            KeyboardButton("🗑️ Mahsulot o'chirish"),
            KeyboardButton("📊 Mahsulot statistikasi"),
            KeyboardButton("🔙 Orqaga")
        )
        
        bot.reply_to(message, "❌ Mahsulot o'chirish bekor qilindi.", reply_markup=markup)
        return
    
    # Kategoriya nomini topish
    category_key = None
    for key, category_data in data['categories'].items():
        if category_data['name'] in message.text:
            category_key = key
            break
    
    if not category_key:
        bot.reply_to(message, "❌ Kategoriya topilmadi! Iltimos, qayta tanlang.")
        return
    
    # Kategoriya mahsulotlarini ko'rsatish
    category_products = data['categories'][category_key]['products']
    
    if not category_products:
        bot.reply_to(message, "❌ Bu kategoriyada mahsulotlar yo'q!")
        return
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    for i, product in enumerate(category_products):
        markup.add(KeyboardButton(f"🗑️ {product['name']} - {product['price']:,} so'm"))
    
    markup.add(KeyboardButton("🔙 Orqaga"))
    
    bot.reply_to(message, 
                 f"🗑️ Qaysi mahsulotni o'chirmoqchisiz?\n\n"
                 f"Kategoriya: {data['categories'][category_key]['name']}",
                 reply_markup=markup)
    
    user_states[message.from_user.id] = "admin_delete_product_select"
    if message.from_user.id not in contact_data:
        contact_data[message.from_user.id] = {}
    contact_data[message.from_user.id]['delete_category'] = category_key

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_edit_product_category")
def handle_admin_edit_product_category(message):
    """Mahsulot tahrirlash uchun kategoriya tanlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Orqaga":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("➕ Mahsulot qo'shish"),
            KeyboardButton("✏️ Mahsulot tahrirlash"),
            KeyboardButton("🗑️ Mahsulot o'chirish"),
            KeyboardButton("📊 Mahsulot statistikasi"),
            KeyboardButton("🔙 Orqaga")
        )
        
        bot.reply_to(message, "❌ Mahsulot tahrirlash bekor qilindi.", reply_markup=markup)
        return
    
    # Kategoriya nomini topish
    category_key = None
    for key, category_data in data['categories'].items():
        if category_data['name'] in message.text:
            category_key = key
            break
    
    if not category_key:
        bot.reply_to(message, "❌ Kategoriya topilmadi! Iltimos, qayta tanlang.")
        return
    
    # Kategoriya mahsulotlarini ko'rsatish
    category_products = data['categories'][category_key]['products']
    
    if not category_products:
        bot.reply_to(message, "❌ Bu kategoriyada mahsulotlar yo'q!")
        return
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    for i, product in enumerate(category_products):
        markup.add(KeyboardButton(f"✏️ {product['name']} - {product['price']:,} so'm"))
    
    markup.add(KeyboardButton("🔙 Orqaga"))
    
    bot.reply_to(message, 
                 f"✏️ Qaysi mahsulotni tahrirlamoqchisiz?\n\n"
                 f"Kategoriya: {data['categories'][category_key]['name']}",
                 reply_markup=markup)
    
    user_states[message.from_user.id] = "admin_edit_product_select"
    if message.from_user.id not in contact_data:
        contact_data[message.from_user.id] = {}
    contact_data[message.from_user.id]['edit_category'] = category_key

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_edit_product_select")
def handle_admin_edit_product_select(message):
    """Mahsulotni tanlash va tahrirlash menyusini ko'rsatish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Orqaga":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'edit_category' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['edit_category']
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("➕ Mahsulot qo'shish"),
            KeyboardButton("✏️ Mahsulot tahrirlash"),
            KeyboardButton("🗑️ Mahsulot o'chirish"),
            KeyboardButton("📊 Mahsulot statistikasi"),
            KeyboardButton("🔙 Orqaga")
        )
        
        bot.reply_to(message, "❌ Mahsulot tahrirlash bekor qilindi.", reply_markup=markup)
        return
    
    # Mahsulot nomini topish
    category_key = contact_data[message.from_user.id]['edit_category']
    category_products = data['categories'][category_key]['products']
    
    product_index = None
    for i, product in enumerate(category_products):
        if product['name'] in message.text:
            product_index = i
            break
    
    if product_index is None:
        bot.reply_to(message, "❌ Mahsulot topilmadi! Iltimos, qayta tanlang.")
        return
    
    # Mahsulot ma'lumotlarini saqlash
    contact_data[message.from_user.id]['edit_product_index'] = product_index
    selected_product = category_products[product_index]
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📝 Nomi"),
        KeyboardButton("💰 Narxi"),
        KeyboardButton("📄 Tavsifi"),
        KeyboardButton("🔢 Miqdori"),
        KeyboardButton("🔙 Orqaga")
    )
    
    bot.reply_to(message, 
                 f"✏️ Mahsulot tahrirlash\n\n"
                 f"📦 Mahsulot: {selected_product['name']}\n"
                 f"💰 Narxi: {selected_product['price']:,} so'm\n"
                 f"📄 Tavsifi: {selected_product['description']}\n"
                 f"🔢 Miqdori: {selected_product['quantity']} ta\n\n"
                 f"Qaysi qismini o'zgartirmoqchisiz?",
                 reply_markup=markup)
    
    user_states[message.from_user.id] = "admin_edit_product_field"

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_edit_product_field")
def handle_admin_edit_product_field(message):
    """Mahsulot qaysi qismini tahrirlashni tanlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Orqaga":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'edit_category' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['edit_category']
        if message.from_user.id in contact_data and 'edit_product_index' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['edit_product_index']
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("➕ Mahsulot qo'shish"),
            KeyboardButton("✏️ Mahsulot tahrirlash"),
            KeyboardButton("🗑️ Mahsulot o'chirish"),
            KeyboardButton("📊 Mahsulot statistikasi"),
            KeyboardButton("🔙 Orqaga")
        )
        
        bot.reply_to(message, "❌ Mahsulot tahrirlash bekor qilindi.", reply_markup=markup)
        return
    
    field = message.text.strip()
    
    if field == "📝 Nomi":
        user_states[message.from_user.id] = "admin_edit_product_name"
        bot.reply_to(message, "📝 Yangi nomni yozing:")
    elif field == "💰 Narxi":
        user_states[message.from_user.id] = "admin_edit_product_price"
        bot.reply_to(message, "💰 Yangi narxni so'mda yozing (masalan: 15000000):")
    elif field == "📄 Tavsifi":
        user_states[message.from_user.id] = "admin_edit_product_description"
        bot.reply_to(message, "📄 Yangi tavsifni yozing:")
    elif field == "🔢 Miqdori":
        user_states[message.from_user.id] = "admin_edit_product_quantity"
        bot.reply_to(message, "🔢 Yangi miqdorni yozing:")
    else:
        bot.reply_to(message, "❌ Noto'g'ri tanlov! Iltimos, qayta tanlang.")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_edit_product_name")
def handle_admin_edit_product_name(message):
    """Mahsulot nomini tahrirlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        category_key = contact_data[message.from_user.id]['edit_category']
        product_index = contact_data[message.from_user.id]['edit_product_index']
        
        # Mahsulot nomini yangilash
        data['categories'][category_key]['products'][product_index]['name'] = message.text.strip()
        
        # data.json ga saqlash
        save_data(data)
        update_products()
        
        success_text = f"""
✅ Mahsulot nomi muvaffaqiyatli o'zgartirildi!

📦 Yangi nom: {message.text.strip()}
        """
        
        bot.reply_to(message, success_text, reply_markup=create_admin_menu())
        
        # Foydalanuvchi holatini tozalash
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'edit_category' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['edit_category']
        if message.from_user.id in contact_data and 'edit_product_index' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['edit_product_index']
            
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik yuz berdi: {e}", reply_markup=create_admin_menu())

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_edit_product_price")
def handle_admin_edit_product_price(message):
    """Mahsulot narxini tahrirlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        price = int(message.text.strip())
        if price <= 0:
            bot.reply_to(message, "❌ Narx 0 dan katta bo'lishi kerak!")
            return
        
        category_key = contact_data[message.from_user.id]['edit_category']
        product_index = contact_data[message.from_user.id]['edit_product_index']
        
        # Mahsulot narxini yangilash
        data['categories'][category_key]['products'][product_index]['price'] = price
        
        # data.json ga saqlash
        save_data(data)
        update_products()
        
        success_text = f"""
✅ Mahsulot narxi muvaffaqiyatli o'zgartirildi!

💰 Yangi narx: {price:,} so'm
        """
        
        bot.reply_to(message, success_text, reply_markup=create_admin_menu())
        
        # Foydalanuvchi holatini tozalash
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'edit_category' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['edit_category']
        if message.from_user.id in contact_data and 'edit_product_index' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['edit_product_index']
            
    except ValueError:
        bot.reply_to(message, "❌ Noto'g'ri narx! Iltimos, raqam kiriting.")
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik yuz berdi: {e}", reply_markup=create_admin_menu())

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_edit_product_description")
def handle_admin_edit_product_description(message):
    """Mahsulot tavsifini tahrirlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        category_key = contact_data[message.from_user.id]['edit_category']
        product_index = contact_data[message.from_user.id]['edit_product_index']
        
        # Mahsulot tavsifini yangilash
        data['categories'][category_key]['products'][product_index]['description'] = message.text.strip()
        
        # data.json ga saqlash
        save_data(data)
        update_products()
        
        success_text = f"""
✅ Mahsulot tavsifi muvaffaqiyatli o'zgartirildi!

📄 Yangi tavsif: {message.text.strip()}
        """
        
        bot.reply_to(message, success_text, reply_markup=create_admin_menu())
        
        # Foydalanuvchi holatini tozalash
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'edit_category' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['edit_category']
        if message.from_user.id in contact_data and 'edit_product_index' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['edit_product_index']
            
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik yuz berdi: {e}", reply_markup=create_admin_menu())

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_edit_product_quantity")
def handle_admin_edit_product_quantity(message):
    """Mahsulot miqdorini tahrirlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        quantity = int(message.text.strip())
        if quantity < 0:
            bot.reply_to(message, "❌ Miqdor 0 dan kam bo'lishi mumkin emas!")
            return
        
        category_key = contact_data[message.from_user.id]['edit_category']
        product_index = contact_data[message.from_user.id]['edit_product_index']
        
        # Mahsulot miqdorini yangilash
        data['categories'][category_key]['products'][product_index]['quantity'] = quantity
        
        # data.json ga saqlash
        save_data(data)
        update_products()
        
        success_text = f"""
✅ Mahsulot miqdori muvaffaqiyatli o'zgartirildi!

🔢 Yangi miqdor: {quantity} ta
        """
        
        bot.reply_to(message, success_text, reply_markup=create_admin_menu())
        
        # Foydalanuvchi holatini tozalash
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'edit_category' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['edit_category']
        if message.from_user.id in contact_data and 'edit_product_index' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['edit_product_index']
            
    except ValueError:
        bot.reply_to(message, "❌ Noto'g'ri miqdor! Iltimos, raqam kiriting.")
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik yuz berdi: {e}", reply_markup=create_admin_menu())

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_delete_product_select")
def handle_admin_delete_product_select(message):
    """Mahsulotni tanlash va o'chirish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Orqaga":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'delete_category' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['delete_category']
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            KeyboardButton("➕ Mahsulot qo'shish"),
            KeyboardButton("✏️ Mahsulot tahrirlash"),
            KeyboardButton("🗑️ Mahsulot o'chirish"),
            KeyboardButton("📊 Mahsulot statistikasi"),
            KeyboardButton("🔙 Orqaga")
        )
        
        bot.reply_to(message, "❌ Mahsulot o'chirish bekor qilindi.", reply_markup=markup)
        return
    
    # Mahsulot nomini topish
    category_key = contact_data[message.from_user.id]['delete_category']
    category_products = data['categories'][category_key]['products']
    
    product_index = None
    for i, product in enumerate(category_products):
        if product['name'] in message.text:
            product_index = i
            break
    
    if product_index is None:
        bot.reply_to(message, "❌ Mahsulot topilmadi! Iltimos, qayta tanlang.")
        return
    
    try:
        # Mahsulotni o'chirish
        deleted_product = data['categories'][category_key]['products'].pop(product_index)
        
        # data.json ga saqlash
        save_data(data)
        
        # Mahsulotlarni yangilash
        update_products()
        
        success_text = f"""
✅ Mahsulot muvaffaqiyatli o'chirildi!

🗑️ Mahsulot: {deleted_product['name']}
💰 Narxi: {deleted_product['price']:,} so'm
🏷️ Kategoriya: {data['categories'][category_key]['name']}
        """
        
        bot.reply_to(message, success_text, reply_markup=create_admin_menu())
        
        # Foydalanuvchi holatini tozalash
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'delete_category' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['delete_category']
        
        # Kategoriya menyusini yangilash
        update_products()
            
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik yuz berdi: {e}", reply_markup=create_admin_menu())

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_add_category_name")
def handle_admin_add_category_name(message):
    """Kategoriya nomini qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Bekor qilish":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        
        bot.reply_to(message, "❌ Kategoriya qo'shish bekor qilindi.", reply_markup=create_admin_menu())
        return
    
    category_name = message.text.strip()
    
    # Kategoriya emoji so'rash
    user_states[message.from_user.id] = "admin_add_category_emoji"
    if message.from_user.id not in contact_data:
        contact_data[message.from_user.id] = {}
    contact_data[message.from_user.id]['new_category'] = {'name': category_name}
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(
        KeyboardButton("📱"), KeyboardButton("💻"), KeyboardButton("👕"),
        KeyboardButton("❄️"), KeyboardButton("🖥️"), KeyboardButton("⌨️"),
        KeyboardButton("🧺"), KeyboardButton("📦"), KeyboardButton("🔧")
    )
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.reply_to(message, 
                 f"✅ Kategoriya nomi: {category_name}\n\n"
                 f"Kategoriya emoji tanlang yoki yozing:",
                 reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_add_category_emoji")
def handle_admin_add_category_emoji(message):
    """Kategoriya emoji qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Bekor qilish":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'new_category' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['new_category']
        
        bot.reply_to(message, "❌ Kategoriya qo'shish bekor qilindi.", reply_markup=create_admin_menu())
        return
    
    emoji = message.text.strip()
    category_name = contact_data[message.from_user.id]['new_category']['name']
    
    # Kategoriya kalitini yaratish
    category_key = category_name.lower().replace(' ', '_').replace('-', '_')
    
    # Kategoriyani qo'shish
    data['categories'][category_key] = {
        'name': category_name,
        'emoji': emoji,
        'products': []
    }
    
    # data.json ga saqlash
    save_data(data)
    
    # Mahsulotlarni yangilash
    update_products()
    
    # Admin uchun xabar
    admin_notification = f"""
🎉 **Yangi kategoriya qo'shildi!**

🏷️ Nomi: {category_name}
📝 Emoji: {emoji}
🔑 Kalit: {category_key}
👤 Qo'shgan: {message.from_user.first_name}
⏰ Vaqt: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """
    
    success_text = f"""
✅ Kategoriya muvaffaqiyatli qo'shildi!

🏷️ Nomi: {category_name}
📝 Emoji: {emoji}
🔑 Kalit: {category_key}

Avtomatik admin panelga o'tmoqda...
    """
    
    # Muvaffaqiyat xabarini ko'rsatish
    bot.reply_to(message, success_text)
    
    # Admin panelga avtomatik qaytish
    admin_text = """
🔧 **Admin Panel**

Quyidagi funksiyalardan birini tanlang:
📊 Statistika - umumiy ma'lumotlar
📦 Mahsulotlar - mahsulotlarni boshqarish
🏷️ Kategoriyalar - kategoriyalarni boshqarish
📋 Buyurtmalar - buyurtmalarni ko'rish
👥 Foydalanuvchilar - foydalanuvchilar ro'yxati
⚙️ Sozlamalar - bot sozlamalari
🗑️ Hammasini o'chirish - barcha ma'lumotlarni o'chirish
    """
    
    # Admin panel uchun keyboard button yaratish
    markup = create_admin_menu()
    
    # Admin panelni yuborish
    bot.send_message(message.chat.id, admin_text, reply_markup=markup)
    
    # Foydalanuvchi holatini tozalash
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]
    if message.from_user.id in contact_data and 'new_category' in contact_data[message.from_user.id]:
        del contact_data[message.from_user.id]['new_category']

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_add_product_name")
def handle_admin_add_product_name(message):
    """Mahsulot nomini qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Bekor qilish":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'new_product' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['new_product']
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_products"))
        
        bot.reply_to(message, "❌ Mahsulot qo'shish bekor qilindi.", reply_markup=markup)
        return
    
    product_name = message.text.strip()
    contact_data[message.from_user.id]['new_product']['name'] = product_name
    user_states[message.from_user.id] = "admin_add_product_price"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.reply_to(message, 
                 f"✅ Mahsulot nomi: {product_name}\n\n"
                 f"Mahsulot narxini so'mda yozing (masalan: 15000000):",
                 reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_add_product_price")
def handle_admin_add_product_price(message):
    """Mahsulot narxini qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Bekor qilish":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'new_product' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['new_product']
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_products"))
        
        bot.reply_to(message, "❌ Mahsulot qo'shish bekor qilindi.", reply_markup=markup)
        return
    
    try:
        price = int(message.text.strip())
        if price <= 0:
            bot.reply_to(message, "❌ Narx 0 dan katta bo'lishi kerak!")
            return
    except ValueError:
        bot.reply_to(message, "❌ Noto'g'ri narx! Iltimos, raqam kiriting.")
        return
    
    contact_data[message.from_user.id]['new_product']['price'] = price
    user_states[message.from_user.id] = "admin_add_product_description"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.reply_to(message, 
                 f"✅ Mahsulot narxi: {price:,} so'm\n\n"
                 f"Mahsulot tavsifini yozing:",
                 reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_add_product_description")
def handle_admin_add_product_description(message):
    """Mahsulot tavsifini qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Bekor qilish":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'new_product' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['new_product']
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_products"))
        
        bot.reply_to(message, "❌ Mahsulot qo'shish bekor qilindi.", reply_markup=markup)
        return
    
    description = message.text.strip()
    contact_data[message.from_user.id]['new_product']['description'] = description
    user_states[message.from_user.id] = "admin_add_product_quantity"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.reply_to(message, 
                 f"✅ Mahsulot tavsifi: {description}\n\n"
                 f"Mahsulot miqdorini yozing (masalan: 10):",
                 reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_add_product_quantity")
def handle_admin_add_product_quantity(message):
    """Mahsulot miqdorini qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Bekor qilish":
        # Bekor qilish
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'new_product' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['new_product']
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="admin_products"))
        
        bot.reply_to(message, "❌ Mahsulot qo'shish bekor qilindi.", reply_markup=markup)
        return
    
    try:
        quantity = int(message.text.strip())
        if quantity < 0:
            bot.reply_to(message, "❌ Miqdor 0 dan kam bo'lishi mumkin emas!")
            return
    except ValueError:
        bot.reply_to(message, "❌ Noto'g'ri miqdor! Iltimos, raqam kiriting.")
        return
    
    # Mahsulotni saqlash
    new_product = contact_data[message.from_user.id]['new_product']
    category_key = new_product['category']
    
    # Ichki kategoriya yoki oddiy kategoriya ekanligini aniqlash
    if '_' in category_key:
        # Ichki kategoriya: category_subcategory
        main_category, subcategory = category_key.split('_', 1)
        if 'products' not in data['categories'][main_category]['subcategories'][subcategory]:
            data['categories'][main_category]['subcategories'][subcategory]['products'] = []
        product_id = f"{subcategory}_{len(data['categories'][main_category]['subcategories'][subcategory]['products']) + 1}"
        category_name = data['categories'][main_category]['subcategories'][subcategory]['name']
    else:
        # Oddiy kategoriya
        if 'products' not in data['categories'][category_key]:
            data['categories'][category_key]['products'] = []
        product_id = f"{category_key}_{len(data['categories'][category_key]['products']) + 1}"
        category_name = data['categories'][category_key]['name']
    
    product_data = {
        'id': product_id,
        'name': new_product['name'],
        'price': new_product['price'],
        'description': new_product['description'],
        'quantity': quantity,
        'parameters': [],
        'characteristics': []
    }
    
    # Mahsulotni to'g'ri joyga qo'shish
    if '_' in category_key:
        # Ichki kategoriyaga qo'shish
        data['categories'][main_category]['subcategories'][subcategory]['products'].append(product_data)
    else:
        # Oddiy kategoriyaga qo'shish
        data['categories'][category_key]['products'].append(product_data)
    
    # data.json ga saqlash
    save_data(data)
    
    # Mahsulotlarni yangilash
    update_products()
    
    # Admin uchun xabar
    admin_notification = f"""
🎉 **Yangi mahsulot qo'shildi!**

📦 Nomi: {product_data['name']}
💰 Narxi: {product_data['price']:,} so'm
📝 Tavsif: {product_data['description']}
🔢 Miqdori: {product_data['quantity']} ta
🏷️ Kategoriya: {category_name}
🆔 ID: {product_id}
👤 Qo'shgan: {message.from_user.first_name}
⏰ Vaqt: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """
    
    success_text = f"""
✅ Mahsulot muvaffaqiyatli qo'shildi!

📦 Nomi: {product_data['name']}
💰 Narxi: {product_data['price']:,} so'm
📝 Tavsif: {product_data['description']}
🔢 Miqdori: {product_data['quantity']} ta
🏷️ Kategoriya: {category_name}
🆔 ID: {product_id}

Avtomatik admin panelga o'tmoqda...
    """
    
    # Muvaffaqiyat xabarini ko'rsatish
    bot.reply_to(message, success_text)
    
    # Xarakteristika qo'shish uchun so'rash
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Xarakteristika qo'shish", callback_data=f"add_char_{product_id}"),
        InlineKeyboardButton("✅ Parametr qo'shish", callback_data=f"add_param_{product_id}"),
        InlineKeyboardButton("🔙 Admin panelga qaytish", callback_data="admin_products")
    )
    
    bot.reply_to(message, 
        f"✅ Mahsulot qo'shildi!\n\n"
        f"📦 {product_data['name']}\n"
        f"💰 {product_data['price']:,} so'm\n\n"
        f"Endi xarakteristika yoki parametr qo'shishingiz mumkin:",
        reply_markup=markup
    )
    
    # Foydalanuvchi holatini tozalash
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]
    if message.from_user.id in contact_data and 'new_product' in contact_data[message.from_user.id]:
        del contact_data[message.from_user.id]['new_product']

# Xarakteristika qo'shish callback handlerlari
@bot.callback_query_handler(func=lambda call: call.data.startswith('add_char_'))
def handle_add_characteristic(call):
    """Xarakteristika qo'shish"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    product_id = call.data.split('add_char_')[1]
    
    # Mahsulotni topish
    product = None
    product_location = None
    
    for category_key, category_data in data['categories'].items():
        if 'subcategories' in category_data:
            for subcategory_key, subcategory_data in category_data['subcategories'].items():
                for i, p in enumerate(subcategory_data.get('products', [])):
                    if p['id'] == product_id:
                        product = p
                        product_location = {
                            'type': 'subcategory',
                            'main_category': category_key,
                            'subcategory': subcategory_key,
                            'index': i
                        }
                        break
                if product:
                    break
            if product:
                break
        else:
            for i, p in enumerate(category_data.get('products', [])):
                if p['id'] == product_id:
                    product = p
                    product_location = {
                        'type': 'category',
                        'category': category_key,
                        'index': i
                    }
                    break
            if product:
                break
    
    if not product:
        bot.answer_callback_query(call.id, "❌ Mahsulot topilmadi!")
        return
    
    # Xarakteristika qo'shish holatini o'rnatish
    user_states[call.from_user.id] = "admin_add_char_name"
    if call.from_user.id not in contact_data:
        contact_data[call.from_user.id] = {}
    contact_data[call.from_user.id]['editing_product'] = {
        'product': product,
        'location': product_location
    }
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.edit_message_text(
        f"📦 **{product['name']}** uchun xarakteristika qo'shish\n\n"
        f"🔧 Xarakteristika nomini yozing (masalan: Ekran o'lchami, Protsessor, Batareya):",
        call.message.chat.id,
        call.message.message_id
    )
    
    bot.send_message(
        call.message.chat.id,
        "🔧 Xarakteristika nomini yozing:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_param_'))
def handle_add_parameter(call):
    """Parametr qo'shish"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    product_id = call.data.split('add_param_')[1]
    
    # Mahsulotni topish (xarakteristika bilan bir xil logika)
    product = None
    product_location = None
    
    for category_key, category_data in data['categories'].items():
        if 'subcategories' in category_data:
            for subcategory_key, subcategory_data in category_data['subcategories'].items():
                for i, p in enumerate(subcategory_data.get('products', [])):
                    if p['id'] == product_id:
                        product = p
                        product_location = {
                            'type': 'subcategory',
                            'main_category': category_key,
                            'subcategory': subcategory_key,
                            'index': i
                        }
                        break
                if product:
                    break
            if product:
                break
        else:
            for i, p in enumerate(category_data.get('products', [])):
                if p['id'] == product_id:
                    product = p
                    product_location = {
                        'type': 'category',
                        'category': category_key,
                        'index': i
                    }
                    break
            if product:
                break
    
    if not product:
        bot.answer_callback_query(call.id, "❌ Mahsulot topilmadi!")
        return
    
    # Parametr qo'shish holatini o'rnatish
    user_states[call.from_user.id] = "admin_add_param_name"
    if call.from_user.id not in contact_data:
        contact_data[call.from_user.id] = {}
    contact_data[call.from_user.id]['editing_product'] = {
        'product': product,
        'location': product_location
    }
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.edit_message_text(
        f"📦 **{product['name']}** uchun parametr qo'shish\n\n"
        f"⚙️ Parametr nomini yozing (masalan: Xotira, Rang, O'lcham):",
        call.message.chat.id,
        call.message.message_id
    )
    
    bot.send_message(
        call.message.chat.id,
        "⚙️ Parametr nomini yozing:",
        reply_markup=markup
    )

# Xarakteristika qo'shish message handlerlari
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_add_char_name")
def handle_admin_add_char_name(message):
    """Xarakteristika nomini qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Bekor qilish":
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'editing_product' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['editing_product']
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Admin panelga qaytish", callback_data="admin_products"))
        bot.reply_to(message, "❌ Xarakteristika qo'shish bekor qilindi.", reply_markup=markup)
        return
    
    char_name = message.text.strip()
    if not char_name:
        bot.reply_to(message, "❌ Xarakteristika nomi bo'sh bo'lishi mumkin emas!")
        return
    
    # Xarakteristika nomini saqlash
    if message.from_user.id not in contact_data:
        contact_data[message.from_user.id] = {}
    contact_data[message.from_user.id]['new_characteristic'] = {'name': char_name}
    
    # Keyingi qadamga o'tish
    user_states[message.from_user.id] = "admin_add_char_value"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.reply_to(message, 
        f"🔧 Xarakteristika nomi: **{char_name}**\n\n"
        f"Endi xarakteristika qiymatini yozing (masalan: 6.1 inch, A17 Pro, 3274 mAh):",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_add_char_value")
def handle_admin_add_char_value(message):
    """Xarakteristika qiymatini qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Bekor qilish":
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'editing_product' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['editing_product']
        if message.from_user.id in contact_data and 'new_characteristic' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['new_characteristic']
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Admin panelga qaytish", callback_data="admin_products"))
        bot.reply_to(message, "❌ Xarakteristika qo'shish bekor qilindi.", reply_markup=markup)
        return
    
    char_value = message.text.strip()
    if not char_value:
        bot.reply_to(message, "❌ Xarakteristika qiymati bo'sh bo'lishi mumkin emas!")
        return
    
    # Xarakteristika qiymatini saqlash
    char_name = contact_data[message.from_user.id]['new_characteristic']['name']
    new_char = {'name': char_name, 'value': char_value}
    
    # Mahsulot ma'lumotlarini olish
    editing_data = contact_data[message.from_user.id]['editing_product']
    product_location = editing_data['location']
    
    # Xarakteristikani mahsulotga qo'shish
    if product_location['type'] == 'subcategory':
        data['categories'][product_location['main_category']]['subcategories'][product_location['subcategory']]['products'][product_location['index']]['characteristics'].append(new_char)
    else:
        data['categories'][product_location['category']]['products'][product_location['index']]['characteristics'].append(new_char)
    
    # data.json ga saqlash
    save_data(data)
    
    # Mahsulotlarni yangilash
    update_products()
    
    # Narxni o'zgartirish so'rash
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💰 Narxni o'zgartirish", callback_data=f"change_price_{editing_data['product']['id']}"),
        InlineKeyboardButton("✅ Boshqa xarakteristika qo'shish", callback_data=f"add_char_{editing_data['product']['id']}"),
        InlineKeyboardButton("🔙 Admin panelga qaytish", callback_data="admin_products")
    )
    
    bot.reply_to(message,
        f"✅ Xarakteristika qo'shildi!\n\n"
        f"🔧 **{char_name}**: {char_value}\n\n"
        f"Xarakteristika qo'shilgandan so'ng narxni ham o'zgartirishingiz mumkin:",
        reply_markup=markup
    )
    
    # Foydalanuvchi holatini tozalash
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]
    if message.from_user.id in contact_data and 'new_characteristic' in contact_data[message.from_user.id]:
        del contact_data[message.from_user.id]['new_characteristic']

# Parametr qo'shish message handlerlari
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_add_param_name")
def handle_admin_add_param_name(message):
    """Parametr nomini qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Bekor qilish":
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'editing_product' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['editing_product']
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Admin panelga qaytish", callback_data="admin_products"))
        bot.reply_to(message, "❌ Parametr qo'shish bekor qilindi.", reply_markup=markup)
        return
    
    param_name = message.text.strip()
    if not param_name:
        bot.reply_to(message, "❌ Parametr nomi bo'sh bo'lishi mumkin emas!")
        return
    
    # Parametr nomini saqlash
    if message.from_user.id not in contact_data:
        contact_data[message.from_user.id] = {}
    contact_data[message.from_user.id]['new_parameter'] = {'name': param_name}
    
    # Keyingi qadamga o'tish
    user_states[message.from_user.id] = "admin_add_param_value"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.reply_to(message, 
        f"⚙️ Parametr nomi: **{param_name}**\n\n"
        f"Endi parametr qiymatini yozing (masalan: 128GB, 256GB, Qora):",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_add_param_value")
def handle_admin_add_param_value(message):
    """Parametr qiymatini qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Bekor qilish":
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'editing_product' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['editing_product']
        if message.from_user.id in contact_data and 'new_parameter' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['new_parameter']
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Admin panelga qaytish", callback_data="admin_products"))
        bot.reply_to(message, "❌ Parametr qo'shish bekor qilindi.", reply_markup=markup)
        return
    
    param_value = message.text.strip()
    if not param_value:
        bot.reply_to(message, "❌ Parametr qiymati bo'sh bo'lishi mumkin emas!")
        return
    
    # Parametr qiymatini saqlash
    param_name = contact_data[message.from_user.id]['new_parameter']['name']
    contact_data[message.from_user.id]['new_parameter']['value'] = param_value
    
    # Keyingi qadamga o'tish - narxni so'rash
    user_states[message.from_user.id] = "admin_add_param_price"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.reply_to(message, 
        f"⚙️ Parametr: **{param_name}**: {param_value}\n\n"
        f"Endi parametr narxini yozing (0 yoki raqam):",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_add_param_price")
def handle_admin_add_param_price(message):
    """Parametr narxini qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Bekor qilish":
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'editing_product' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['editing_product']
        if message.from_user.id in contact_data and 'new_parameter' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['new_parameter']
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Admin panelga qaytish", callback_data="admin_products"))
        bot.reply_to(message, "❌ Parametr qo'shish bekor qilindi.", reply_markup=markup)
        return
    
    try:
        param_price = int(message.text.strip())
        if param_price < 0:
            bot.reply_to(message, "❌ Narx manfiy bo'lishi mumkin emas!")
            return
    except ValueError:
        bot.reply_to(message, "❌ Noto'g'ri narx! Iltimos, raqam kiriting.")
        return
    
    # Parametr ma'lumotlarini olish
    param_data = contact_data[message.from_user.id]['new_parameter']
    new_param = {
        'name': param_data['name'], 
        'value': param_data['value'], 
        'price': param_price
    }
    
    # Mahsulot ma'lumotlarini olish
    editing_data = contact_data[message.from_user.id]['editing_product']
    product_location = editing_data['location']
    
    # Parametrni mahsulotga qo'shish
    if product_location['type'] == 'subcategory':
        data['categories'][product_location['main_category']]['subcategories'][product_location['subcategory']]['products'][product_location['index']]['parameters'].append(new_param)
    else:
        data['categories'][product_location['category']]['products'][product_location['index']]['parameters'].append(new_param)
    
    # data.json ga saqlash
    save_data(data)
    
    # Mahsulotlarni yangilash
    update_products()
    
    # Narxni o'zgartirish so'rash
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💰 Narxni o'zgartirish", callback_data=f"change_price_{editing_data['product']['id']}"),
        InlineKeyboardButton("✅ Boshqa parametr qo'shish", callback_data=f"add_param_{editing_data['product']['id']}"),
        InlineKeyboardButton("🔙 Admin panelga qaytish", callback_data="admin_products")
    )
    
    price_text = f" (+{param_price:,} so'm)" if param_price > 0 else " (bepul)"
    
    bot.reply_to(message,
        f"✅ Parametr qo'shildi!\n\n"
        f"⚙️ **{new_param['name']}**: {new_param['value']}{price_text}\n\n"
        f"Parametr qo'shilgandan so'ng narxni ham o'zgartirishingiz mumkin:",
        reply_markup=markup
    )
    
    # Foydalanuvchi holatini tozalash
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]
    if message.from_user.id in contact_data and 'new_parameter' in contact_data[message.from_user.id]:
        del contact_data[message.from_user.id]['new_parameter']

# Narxni o'zgartirish callback handler
@bot.callback_query_handler(func=lambda call: call.data.startswith('change_price_'))
def handle_change_price(call):
    """Narxni o'zgartirish"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    product_id = call.data.split('change_price_')[1]
    
    # Mahsulotni topish
    product = None
    product_location = None
    
    for category_key, category_data in data['categories'].items():
        if 'subcategories' in category_data:
            for subcategory_key, subcategory_data in category_data['subcategories'].items():
                for i, p in enumerate(subcategory_data.get('products', [])):
                    if p['id'] == product_id:
                        product = p
                        product_location = {
                            'type': 'subcategory',
                            'main_category': category_key,
                            'subcategory': subcategory_key,
                            'index': i
                        }
                        break
                if product:
                    break
            if product:
                break
        else:
            for i, p in enumerate(category_data.get('products', [])):
                if p['id'] == product_id:
                    product = p
                    product_location = {
                        'type': 'category',
                        'category': category_key,
                        'index': i
                    }
                    break
            if product:
                break
    
    if not product:
        bot.answer_callback_query(call.id, "❌ Mahsulot topilmadi!")
        return
    
    # Narxni o'zgartirish holatini o'rnatish
    user_states[call.from_user.id] = "admin_change_price"
    if call.from_user.id not in contact_data:
        contact_data[call.from_user.id] = {}
    contact_data[call.from_user.id]['editing_product'] = {
        'product': product,
        'location': product_location
    }
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.edit_message_text(
        f"📦 **{product['name']}**\n"
        f"💰 Hozirgi narx: {product['price']:,} so'm\n\n"
        f"Yangi narxni yozing (faqat raqam):",
        call.message.chat.id,
        call.message.message_id
    )
    
    bot.send_message(
        call.message.chat.id,
        "💰 Yangi narxni yozing:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_change_price")
def handle_admin_change_price(message):
    """Narxni o'zgartirish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Bekor qilish":
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'editing_product' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['editing_product']
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Admin panelga qaytish", callback_data="admin_products"))
        bot.reply_to(message, "❌ Narxni o'zgartirish bekor qilindi.", reply_markup=markup)
        return
    
    try:
        new_price = int(message.text.strip())
        if new_price <= 0:
            bot.reply_to(message, "❌ Narx 0 dan katta bo'lishi kerak!")
            return
    except ValueError:
        bot.reply_to(message, "❌ Noto'g'ri narx! Iltimos, raqam kiriting.")
        return
    
    # Mahsulot ma'lumotlarini olish
    editing_data = contact_data[message.from_user.id]['editing_product']
    product_location = editing_data['location']
    old_price = editing_data['product']['price']
    
    # Narxni o'zgartirish
    if product_location['type'] == 'subcategory':
        data['categories'][product_location['main_category']]['subcategories'][product_location['subcategory']]['products'][product_location['index']]['price'] = new_price
    else:
        data['categories'][product_location['category']]['products'][product_location['index']]['price'] = new_price
    
    # data.json ga saqlash
    save_data(data)
    
    # Mahsulotlarni yangilash
    update_products()
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Admin panelga qaytish", callback_data="admin_products"))
    
    bot.reply_to(message,
        f"✅ Narx muvaffaqiyatli o'zgartirildi!\n\n"
        f"📦 **{editing_data['product']['name']}**\n"
        f"💰 Eski narx: {old_price:,} so'm\n"
        f"💰 Yangi narx: {new_price:,} so'm\n"
        f"📈 O'zgarish: {new_price - old_price:,} so'm",
        reply_markup=markup
    )
    
    # Foydalanuvchi holatini tozalash
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]
    if message.from_user.id in contact_data and 'editing_product' in contact_data[message.from_user.id]:
        del contact_data[message.from_user.id]['editing_product']

# Yangi callback handlerlar
@bot.callback_query_handler(func=lambda call: call.data == "go_to_admin_panel")
def go_to_admin_panel(call):
    """Admin panelga o'tish"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    admin_text = """
🔧 **Admin Panel**

Quyidagi funksiyalardan birini tanlang:
📊 Statistika - umumiy ma'lumotlar
📦 Mahsulotlar - mahsulotlarni boshqarish
🏷️ Kategoriyalar - kategoriyalarni boshqarish
📋 Buyurtmalar - buyurtmalarni ko'rish
👥 Foydalanuvchilar - foydalanuvchilar ro'yxati
⚙️ Sozlamalar - bot sozlamalari
🗑️ Hammasini o'chirish - barcha ma'lumotlarni o'chirish
    """
    
    # Admin panel uchun keyboard button yaratish
    markup = create_admin_menu()
    
    bot.send_message(call.message.chat.id, admin_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_product_to_"))
def add_product_to_category(call):
    """Kategoriyaga mahsulot qo'shish"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    category_key = call.data.split("add_product_to_")[1]
    
    # Foydalanuvchi holatini saqlash
    user_states[call.from_user.id] = "admin_add_product_name"
    if call.from_user.id not in contact_data:
        contact_data[call.from_user.id] = {}
    contact_data[call.from_user.id]['new_product'] = {'category': category_key}
    
    category_name = data['categories'][category_key]['name']
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.edit_message_text(
        f"📦 Yangi mahsulot qo'shish\n\n"
        f"Kategoriya: {category_name}\n\n"
        f"Mahsulot nomini yozing:",
        call.message.chat.id, call.message.message_id
    )
    
    bot.send_message(
        call.message.chat.id,
        "📝 Mahsulot nomini yozing:",
        reply_markup=markup
    )

# Admin panel callback handlerlari
@bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
def admin_stats_callback(call):
    """Admin statistika callback"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    total_users = len(data['users'])
    total_orders = len(data['orders'])
    total_products = sum(len(cat['products']) for cat in data['categories'].values())
    total_categories = len(data['categories'])
    
    # Bugungi buyurtmalar
    today = datetime.now().strftime("%Y-%m-%d")
    today_orders = [order for order in data['orders'] if order['date'].startswith(today)]
    
    stats_text = f"""
📊 **Bot Statistikasi**

👥 **Foydalanuvchilar:**
• Jami: {total_users} ta
• Bugun faol: {len(today_orders)} ta

📦 **Mahsulotlar:**
• Kategoriyalar: {total_categories} ta
• Mahsulotlar: {total_products} ta

📋 **Buyurtmalar:**
• Jami: {total_orders} ta
• Bugun: {len(today_orders)} ta

💰 **Bugungi tushum:**
• {sum(order.get('total', 0) for order in today_orders):,} so'm
    """
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="go_to_admin_panel"))
    
    bot.edit_message_text(stats_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_products")
def admin_products_callback(call):
    """Admin mahsulotlar callback"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    products_text = """
📦 **Mahsulotlar Boshqaruvi**

Quyidagi amallardan birini tanlang:
➕ Mahsulot qo'shish - yangi mahsulot qo'shish
✏️ Mahsulot tahrirlash - mavjud mahsulotni o'zgartirish
🗑️ Mahsulot o'chirish - mahsulotni o'chirish
📊 Mahsulot statistikasi - mahsulotlar haqida ma'lumot
    """
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ Mahsulot qo'shish", callback_data="admin_add_product"),
        InlineKeyboardButton("✏️ Mahsulot tahrirlash", callback_data="admin_edit_product"),
        InlineKeyboardButton("🗑️ Mahsulot o'chirish", callback_data="admin_delete_product"),
        InlineKeyboardButton("📊 Mahsulot statistikasi", callback_data="admin_product_stats")
    )
    markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="go_to_admin_panel"))
    
    bot.edit_message_text(products_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_categories")
def admin_categories_callback(call):
    """Admin kategoriyalar callback"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    categories_text = f"""
🏷️ **Kategoriyalar Boshqaruvi**

Jami kategoriyalar: {len(data['categories'])} ta

Quyidagi amallardan birini tanlang:
➕ Kategoriya qo'shish - yangi kategoriya qo'shish
✏️ Kategoriya tahrirlash - mavjud kategoriyani o'zgartirish
🗑️ Kategoriya o'chirish - kategoriyani o'chirish
    """
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ Kategoriya qo'shish", callback_data="admin_add_category"),
        InlineKeyboardButton("✏️ Kategoriya tahrirlash", callback_data="admin_edit_category"),
        InlineKeyboardButton("🗑️ Kategoriya o'chirish", callback_data="admin_delete_category")
    )
    markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="go_to_admin_panel"))
    
    bot.edit_message_text(categories_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_orders")
def admin_orders_callback(call):
    """Admin buyurtmalar callback"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    if not data['orders']:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="go_to_admin_panel"))
        bot.edit_message_text("📋 Hali buyurtmalar yo'q!", call.message.chat.id, call.message.message_id, reply_markup=markup)
        return
    
    # Oxirgi 5 ta buyurtmani ko'rsatish
    recent_orders = data['orders'][-5:]
    
    orders_text = f"""
📋 **Buyurtmalar Boshqaruvi**

Jami buyurtmalar: {len(data['orders'])} ta

**Oxirgi buyurtmalar:**
"""
    
    for i, order in enumerate(reversed(recent_orders), 1):
        orders_text += f"""
{i}. 📦 Buyurtma #{len(data['orders']) - len(recent_orders) + i}
   👤 {order.get('customer_name', 'Noma lum')}
   📱 {order.get('customer_phone', 'Noma lum')}
   💰 {order.get('total', 0):,} so'm
   📅 {order.get('date', 'Noma lum')}
"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📋 Barcha buyurtmalar", callback_data="admin_all_orders"),
        InlineKeyboardButton("🗑️ Buyurtma o'chirish", callback_data="admin_delete_order")
    )
    markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="go_to_admin_panel"))
    
    bot.edit_message_text(orders_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_users")
def admin_users_callback(call):
    """Admin foydalanuvchilar callback"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    if not data['users']:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="go_to_admin_panel"))
        bot.edit_message_text("👥 Hali foydalanuvchilar yo'q!", call.message.chat.id, call.message.message_id, reply_markup=markup)
        return
    
    # Oxirgi 5 ta foydalanuvchini ko'rsatish
    recent_users = data['users'][-5:]
    
    users_text = f"""
👥 **Foydalanuvchilar Boshqaruvi**

Jami foydalanuvchilar: {len(data['users'])} ta

**Oxirgi ro'yxatdan o'tganlar:**
"""
    
    for i, user in enumerate(reversed(recent_users), 1):
        username = user.get('username', 'Noma lum')
        first_name = user.get('first_name', 'Noma lum')
        joined_date = user.get('joined_date', 'Noma lum')
        
        users_text += f"""
{i}. 👤 {first_name} (@{username})
   📅 {joined_date}
"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👥 Barcha foydalanuvchilar", callback_data="admin_all_users"),
        InlineKeyboardButton("🗑️ Foydalanuvchi o'chirish", callback_data="admin_delete_user")
    )
    markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="go_to_admin_panel"))
    
    bot.edit_message_text(users_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_settings")
def admin_settings_callback(call):
    """Admin sozlamalar callback"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    settings_text = f"""
⚙️ **Bot Sozlamalari**

🔑 **Bot Token:** {data['settings']['bot_token']}
👤 **Admin ID:** {data['settings']['admin_id']}

💳 **To'lov ma'lumotlari:**
🏦 Karta raqam: {data['settings']['payment_card']}
👤 Mulkdor: {data['settings']['payment_owner']}
🏛️ Bank: {data['settings']['payment_bank']}
    """
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔑 Token o'zgartirish", callback_data="admin_change_token"),
        InlineKeyboardButton("👤 Admin ID o'zgartirish", callback_data="admin_change_admin"),
        InlineKeyboardButton("💳 To'lov ma'lumotlari", callback_data="admin_change_payment")
    )
    markup.add(InlineKeyboardButton("🔙 Orqaga", callback_data="go_to_admin_panel"))
    
    bot.edit_message_text(settings_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_delete_all")
def admin_delete_all_callback(call):
    """Admin hammasini o'chirish callback"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    warning_text = """
⚠️ **OGOHLANTIRISH!**

Siz barcha kategoriyalar va mahsulotlarni o'chirmoqchisiz!

Bu amal qaytarib bo'lmaydi va barcha ma'lumotlar yo'qoladi:
🗑️ Barcha kategoriyalar
🗑️ Barcha mahsulotlar
🗑️ Barcha buyurtmalar
🗑️ Barcha foydalanuvchilar

Davom etishni xohlaysizmi?
    """
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Ha, hammasini o'chir", callback_data="admin_confirm_delete_all"),
        InlineKeyboardButton("❌ Yo'q, bekor qil", callback_data="go_to_admin_panel")
    )
    
    bot.edit_message_text(warning_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

# Ichki kategoriya qo'shish jarayoni
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_add_subcategory_category")
def handle_admin_add_subcategory_category(message):
    """Ichki kategoriya uchun asosiy kategoriya tanlash"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Orqaga":
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        
        bot.reply_to(message, "❌ Ichki kategoriya qo'shish bekor qilindi.", reply_markup=create_admin_menu())
        return
    
    # Kategoriya nomini topish
    category_key = None
    for key, category_data in data['categories'].items():
        if category_data['name'] in message.text:
            category_key = key
            break
    
    if not category_key:
        bot.reply_to(message, "❌ Kategoriya topilmadi! Iltimos, qayta tanlang.")
        return
    
    # Kategoriya ma'lumotlarini saqlash
    if message.from_user.id not in contact_data:
        contact_data[message.from_user.id] = {}
    contact_data[message.from_user.id]['parent_category'] = category_key
    
    # Ichki kategoriya nomini so'rash
    user_states[message.from_user.id] = "admin_add_subcategory_name"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.reply_to(message, 
                 f"📁 Yangi ichki kategoriya qo'shish\n\n"
                 f"📂 Asosiy kategoriya: {data['categories'][category_key]['name']}\n\n"
                 f"Ichki kategoriya nomini yozing (masalan: Telefonlar):",
                 reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_add_subcategory_name")
def handle_admin_add_subcategory_name(message):
    """Ichki kategoriya nomini qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Bekor qilish":
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'parent_category' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['parent_category']
        
        bot.reply_to(message, "❌ Ichki kategoriya qo'shish bekor qilindi.", reply_markup=create_admin_menu())
        return
    
    subcategory_name = message.text.strip()
    
    # Ichki kategoriya emoji so'rash
    user_states[message.from_user.id] = "admin_add_subcategory_emoji"
    contact_data[message.from_user.id]['new_subcategory'] = {'name': subcategory_name}
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(
        KeyboardButton("📱"), KeyboardButton("💻"), KeyboardButton("👕"),
        KeyboardButton("❄️"), KeyboardButton("🖥️"), KeyboardButton("⌨️"),
        KeyboardButton("🧺"), KeyboardButton("📦"), KeyboardButton("🔧")
    )
    markup.add(KeyboardButton("❌ Bekor qilish"))
    
    bot.reply_to(message, 
                 f"✅ Ichki kategoriya nomi: {subcategory_name}\n\n"
                 f"Ichki kategoriya emoji tanlang yoki yozing:",
                 reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "admin_add_subcategory_emoji")
def handle_admin_add_subcategory_emoji(message):
    """Ichki kategoriya emoji qabul qilish"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "❌ Bekor qilish":
        if message.from_user.id in user_states:
            del user_states[message.from_user.id]
        if message.from_user.id in contact_data and 'new_subcategory' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['new_subcategory']
        if message.from_user.id in contact_data and 'parent_category' in contact_data[message.from_user.id]:
            del contact_data[message.from_user.id]['parent_category']
        
        bot.reply_to(message, "❌ Ichki kategoriya qo'shish bekor qilindi.", reply_markup=create_admin_menu())
        return
    
    emoji = message.text.strip()
    subcategory_name = contact_data[message.from_user.id]['new_subcategory']['name']
    parent_category = contact_data[message.from_user.id]['parent_category']
    
    # Ichki kategoriya kalitini yaratish
    subcategory_key = subcategory_name.lower().replace(' ', '_').replace('-', '_')
    
    # Ichki kategoriyani qo'shish
    if 'subcategories' not in data['categories'][parent_category]:
        data['categories'][parent_category]['subcategories'] = {}
    
    data['categories'][parent_category]['subcategories'][subcategory_key] = {
        'name': subcategory_name,
        'emoji': emoji,
        'products': []
    }
    
    # data.json ga saqlash
    save_data(data)
    
    # Mahsulotlarni yangilash
    update_products()
    
    # Muvaffaqiyat xabari
    success_text = f"""
✅ Ichki kategoriya muvaffaqiyatli qo'shildi!

📁 Nomi: {subcategory_name}
😀 Emoji: {emoji}
🔑 Kalit: {subcategory_key}
📂 Asosiy kategoriya: {data['categories'][parent_category]['name']}
    """
    
    bot.reply_to(message, success_text, reply_markup=create_admin_menu())
    
    # Foydalanuvchi holatini tozalash
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]
    if message.from_user.id in contact_data and 'new_subcategory' in contact_data[message.from_user.id]:
        del contact_data[message.from_user.id]['new_subcategory']
    if message.from_user.id in contact_data and 'parent_category' in contact_data[message.from_user.id]:
        del contact_data[message.from_user.id]['parent_category']

# Botni ishga tushirish
if __name__ == "__main__":
    print("🤖 Bot ishga tushdi...")
    print(f"👤 Admin ID: {ADMIN_ID}")
    print(f"🔑 Bot Token: {BOT_TOKEN}")
    print("📊 Admin panel: /admin")
    print("✅ Barcha ma'lumotlar data.json ga saqlanadi!")
    bot.polling(none_stop=True)