# AUX Shop Telegram Bot

Bu Telegram bot online do'kon uchun yaratilgan bo'lib, mahsulotlarni ko'rish, buyurtma berish va admin panel orqali boshqarish imkoniyatlarini beradi.

## 🚀 O'rnatish va ishga tushirish

### 1. Kerakli paketlarni o'rnatish
```bash
pip3 install -r requirements.txt
```

### 2. Bot tokenini sozlash
`data.json` faylida bot tokenini o'zgartiring:
```json
{
  "settings": {
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "admin_id": YOUR_ADMIN_ID
  }
}
```

### 3. Botni ishga tushirish
```bash
python3 main.py
```

## 📱 Bot funksiyalari

### Foydalanuvchilar uchun:
- 🛍️ **Kategoriyalar** - Mahsulotlarni kategoriyalar bo'yicha ko'rish
- 🔍 **Qidiruv** - Mahsulotlarni qidirish
- 🛒 **Savat** - Tanlangan mahsulotlarni ko'rish va buyurtma berish
- 🌐 **Til** - Bot tilini o'zgartirish (O'zbekcha, Русский, English)
- 📋 **Buyurtmalar** - Buyurtmalar tarixini ko'rish
- 📞 **Aloqa** - Operator bilan bog'lanish

### Admin uchun:
- 📊 **Statistika** - Bot statistikasini ko'rish
- 📦 **Mahsulotlar** - Mahsulotlarni boshqarish
- 🏷️ **Kategoriyalar** - Kategoriyalarni boshqarish
- 📋 **Buyurtmalar** - Buyurtmalarni ko'rish va boshqarish
- 👥 **Foydalanuvchilar** - Foydalanuvchilarni boshqarish
- ⚙️ **Sozlamalar** - Bot sozlamalarini o'zgartirish

## 🛠️ Admin komandalari

- `/start` - Botni boshlash
- `/admin` - Admin panelga kirish

## 📁 Fayl tuzilishi

```
aux-bot/
├── main.py          # Asosiy bot kodi
├── data.json        # Ma'lumotlar bazasi
├── requirements.txt # Kerakli paketlar
└── README.md        # Bu fayl
```

## 💾 Ma'lumotlar saqlash

Barcha ma'lumotlar `data.json` faylida saqlanadi:
- Kategoriyalar va mahsulotlar
- Foydalanuvchilar
- Buyurtmalar
- Bot sozlamalari

## 🔧 Admin panel

Admin panel orqali quyidagi amallarni bajarishingiz mumkin:

### Kategoriyalar:
- ➕ Kategoriya qo'shish
- ✏️ Kategoriya tahrirlash
- 🗑️ Kategoriya o'chirish

### Mahsulotlar:
- ➕ Mahsulot qo'shish
- ✏️ Mahsulot tahrirlash
- 🗑️ Mahsulot o'chirish

### Buyurtmalar:
- 📋 Barcha buyurtmalarni ko'rish
- ✅ Buyurtmalarni tasdiqlash
- ❌ Buyurtmalarni rad etish

## 🌐 Qo'llab-quvvatlanadigan tillar

- 🇺🇿 O'zbekcha
- 🇷🇺 Русский  
- 🇺🇸 English

## 💳 To'lov usullari

- 💳 Karta bilan to'lov
- 💵 Naqd pul

## 📞 Aloqa

Bot orqali operator bilan bog'lanish uchun "📞 Aloqa" tugmasini bosing va savolingizni yozing.

## ⚠️ Eslatma

- Bot faqat admin ID si ko'rsatilgan foydalanuvchi uchun admin panel ochiq
- Barcha ma'lumotlar `data.json` faylida saqlanadi
- Bot ishga tushganda avtomatik ravishda namuna ma'lumotlar qo'shiladi

## 🚀 Ishga tushirish

```bash
# 1. Paketlarni o'rnatish
pip3 install -r requirements.txt

# 2. Bot tokenini sozlash (data.json da)
# 3. Botni ishga tushirish
python3 main.py
```

Bot ishga tushgandan so'ng Telegram da `/start` komandasini yuboring!
