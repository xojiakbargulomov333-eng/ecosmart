"""
🤖 EcoSmart Grid Global - Final Executive Edition
Version: 7.0 (The Ultimate Masterpiece)
"""

import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ============================================
# CONFIGURATION
# ============================================

BOT_TOKEN = "7892538649:AAEM6rZIMfsqIW5Y1GCDqbb3vTx8R69A9xM"

# Foydalanuvchi ma'lumotlar bazasi (Simulyatsiya)
user_data = {}

STRINGS = {
    'uz': {
        'welcome': "🏛 <b>EcoSmart Grid: Davlat Boshqaruv Markazi</b>\n\nFoydalanuvchi: <code>{user}</code>\nID: <code>{acc}</code>\n\nBarcha kommunal xizmatlar va energiya monitoringi yagona raqamli platformada.",
        'btn_billing': "🧾 Kommunal Billing",
        'btn_stats': "📊 Sarfiyat Analitikasi",
        'btn_weather': "☁️ Ob-havo & Quyosh",
        'btn_lang': "🌐 Tilni O'zgartirish",
        'btn_back': "◀️ Orqaga",
        'billing_title': "🧾 <b>KOMMUNAL HISOBLAR</b>",
        'electric': "⚡ Elektr",
        'gas': "🔥 Gaz",
        'water': "💧 Suv",
        'waste': "♻️ Chiqindi",
        'stats_title': "📊 <b>SARFIYAT GRAFIGI (30 kun)</b>",
        'weather_title': "☁️ <b>OB-HAVO VA ENERGIYA BASHORATI</b>",
        'currency': "so'm",
        'debt_msg': "🔴 Qarzdorlik: ",
        'no_debt': "✅ Qarzdorlik mavjud emas"
    },
    'ru': {
        'welcome': "🏛 <b>EcoSmart Grid: Государственный Центр Управления</b>\n\nПользователь: <code>{user}</code>\nID: <code>{acc}</code>\n\nВсе услуги и мониторинг энергии на единой платформе.",
        'btn_billing': "🧾 Коммунальный Биллинг",
        'btn_stats': "📊 Аналитика Расхода",
        'btn_weather': "☁️ Погода и Солнце",
        'btn_lang': "🌐 Сменить язык",
        'btn_back': "◀️ Назад",
        'billing_title': "🧾 <b>КОММУНАЛЬНЫЕ СЧЕТА</b>",
        'electric': "⚡ Электро",
        'gas': "🔥 Газ",
        'water': "💧 Вода",
        'waste': "♻️ Мусор",
        'stats_title': "📊 <b>ГРАФИК РАСХОДА (30 дней)</b>",
        'weather_title': "☁️ <b>ПРОГНОЗ ПОГОДЫ И ЭНЕРГИИ</b>",
        'currency': "сум",
        'debt_msg': "🔴 Задолженность: ",
        'no_debt': "✅ Задолженностей нет"
    },
    'en': {
        'welcome': "🏛 <b>EcoSmart Grid: Executive Control Center</b>\n\nUser: <code>{user}</code>\nID: <code>{acc}</code>\n\nCentralized utility billing and energy monitoring platform.",
        'btn_billing': "🧾 Utility Billing",
        'btn_stats': "📊 Usage Analytics",
        'btn_weather': "☁️ Weather & Solar",
        'btn_lang': "🌐 Change Language",
        'btn_back': "◀️ Back",
        'billing_title': "🧾 <b>UTILITY BILLING REPORT</b>",
        'electric': "⚡ Electric",
        'gas': "🔥 Gas",
        'water': "💧 Water",
        'waste': "♻️ Waste",
        'stats_title': "📊 <b>USAGE CHART (30 Days)</b>",
        'weather_title': "☁️ <b>WEATHER & ENERGY FORECAST</b>",
        'currency': "UZS",
        'debt_msg': "🔴 Debt: ",
        'no_debt': "✅ No outstanding debt"
    }
}

# ============================================
# ANALYTICS ENGINE
# ============================================

def generate_text_chart():
    """Vazirlik uchun vizual tekstli grafik"""
    bars = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
    chart = ""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    for m in months:
        val = random.randint(3, 15)
        chart += f"<code>{m}</code> | {'█' * val} {val*10}kWh\n"
    return chart

# ============================================
# HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data='lang_uz')],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("🇺🇸 English", callback_data='lang_en')]
    ])
    text = "🌐 Please select a language / Tilni tanlang / Выберите язык:"
    if update.message:
        await update.message.reply_text(text, reply_markup=keyboard)
    else:
        await update.callback_query.message.edit_text(text, reply_markup=keyboard)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    data = query.data

    if data.startswith('lang_'):
        user_data[uid] = data.split('_')[1]
        lang = user_data[uid]
        s = STRINGS[lang]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(s['btn_billing'], callback_data='nav_billing')],
            [InlineKeyboardButton(s['btn_stats'], callback_data='nav_stats')],
            [InlineKeyboardButton(s['btn_weather'], callback_data='nav_weather')],
            [InlineKeyboardButton(s['btn_lang'], callback_data='nav_lang_change')]
        ])
        await query.message.edit_text(s['welcome'].format(user=query.from_user.first_name, acc=f"ID-{uid % 10000}"), 
                                    parse_mode='HTML', reply_markup=keyboard)
        return

    lang = user_data.get(uid, 'uz')
    s = STRINGS[lang]

    if data == 'nav_billing':
        # Simulyatsiya qilingan balanslar
        bal = {'e': 45000, 'g': -12000, 'w': 8000, 'r': 0}
        report = f"{s['billing_title']}\n━━━━━━━━━━━━━━━━━━━━\n" \
                 f"{s['electric']}: {bal['e']:,} {s['currency']}\n" \
                 f"{s['gas']}: {bal['g']:,} {s['currency']}\n" \
                 f"{s['water']}: {bal['w']:,} {s['currency']}\n" \
                 f"{s['waste']}: {bal['r']:,} {s['currency']}\n" \
                 f"━━━━━━━━━━━━━━━━━━━━\n"
        report += f"{s['debt_msg']} {abs(bal['g']):,} {s['currency']}" if bal['g'] < 0 else s['no_debt']
        
        await query.message.edit_text(report, parse_mode='HTML', 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(s['btn_back'], callback_data=f'lang_{lang}')]]))

    elif data == 'nav_stats':
        chart = generate_text_chart()
        text = f"{s['stats_title']}\n━━━━━━━━━━━━━━━━━━━━\n{chart}\n<i>Trend: Energiya tejamkorligi 12% ga oshgan.</i>"
        await query.message.edit_text(text, parse_mode='HTML', 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(s['btn_back'], callback_data=f'lang_{lang}')]]))

    elif data == 'nav_weather':
        temp = random.randint(28, 35)
        solar = random.randint(80, 100)
        text = f"{s['weather_title']}\n━━━━━━━━━━━━━━━━━━━━\n" \
               f"🌡 Harorat: {temp}°C\n" \
               f"☀️ Quyosh aktivligi: {solar}%\n" \
               f"⚡ Kutilayotgan generatsiya: {(solar * 0.15):.1f} kWh"
        await query.message.edit_text(text, parse_mode='HTML', 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(s['btn_back'], callback_data=f'lang_{lang}')]]))

    elif data == 'nav_lang_change':
        await start(update, context)

# ============================================
# RUN
# ============================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()

if __name__ == '__main__':
    main()
