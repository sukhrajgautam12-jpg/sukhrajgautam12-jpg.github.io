import os
import telebot
import requests
import sqlite3
from datetime import datetime

API_TOKEN = ':8275446717:AAE-8cGkDQYXhWhNIQU9CjOoSMXiPRFujRc'
bot = telebot.TeleBot(API_TOKEN)
DAILY_LIMIT = 3

conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, telegram_id INTEGER, username TEXT, uid TEXT, region TEXT, timestamp TEXT, date_only TEXT)''')
conn.commit()
conn.close()

@bot.message_handler(commands=['like'])
def handle_like(message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "❌ **Usage:** `/like {region} {uid}`\nExample: `/like ind 5513136279`", parse_mode='Markdown')
        return
    region = args[1]
    uid = args[2]
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('SELECT COUNT(*) FROM users WHERE telegram_id = ? AND date_only = ?', (user_id, today))
    used_today = cursor.fetchone()[0]
    conn.close()
    if used_today >= DAILY_LIMIT:
        bot.reply_to(message, f"⚠️ **Limit Exceeded!**\nAapki aaj ki limit ({DAILY_LIMIT} likes) khatam ho gayi hai.", parse_mode='Markdown')
        return
    sent_msg = bot.reply_to(message, "⏳ *Processing your request...*", parse_mode='Markdown')
    api_url = f"https://vercel.app{uid}&server_name={region}&key=NJM"
    try:
        response = requests.get(api_url)
        data = response.json()
        name = data.get('PlayerNickname', 'N/A')
        likes_before = data.get('LikesbeforeCommand', '0')
        likes_given = data.get('LikesGivenByAPI', '0')
        likes_after = data.get('LikesafterCommand', '0')
        remaining = data.get('remains', 'N/A')
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('INSERT INTO users (telegram_id, username, uid, region, timestamp, date_only) VALUES (?, ?, ?, ?, ?, ?)', (user_id, message.from_user.username, uid, region, current_time, today))
        conn.commit()
        conn.close()
        banner_url = f"https://najmi-ob53-like-api-vvkb.vercelapp{uid}&server_name={region}"
        remains_today = DAILY_LIMIT - (used_today + 1)
        template = f"╔════════◇◆◇════════╗\n    🎉 LIKE SUCCESSFULLY 👍 \n╚════════◇◆◇════════╝\n👑 **Name:** {name}\n🕹️ **UID:** {uid}\n🌐 **Region:** {region.upper()}\n━━━━━━━━━━━━━━━━━━━━━\n❤️ **Likes Before:** {likes_before}\n🩵 **Likes Given:** {likes_given}\n💚 **Likes after:** {likes_after}\n━━━━━━━━━━━━━━━━━━━━━\n📊 **Your Daily Remaining:** {remains_today}/{DAILY_LIMIT}\n🌍 **API Remaining:** {remaining}"
        bot.delete_message(chat_id=message.chat.id, message_id=sent_msg.message_id)
        try:
            bot.send_photo(chat_id=message.chat.id, photo=banner_url, caption=template, parse_mode='Markdown')
        except:
            bot.send_message(chat_id=message.chat.id, text=template, parse_mode='Markdown')
    except Exception as e:
        bot.edit_message_text(f"❌ **Error Connection to API**\n`{str(e)}`", chat_id=message.chat.id, message_id=sent_msg.message_id, parse_mode='Markdown')

if __name__ == "__main__":
    print("Bot is online...")
    bot.infinity_polling()
