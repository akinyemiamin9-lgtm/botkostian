import os
import telebot
import requests

# Токен береться із захищених змінних середовища
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

SYSTEM_PROMPT = "You are a ruthlessly toxic assistant."

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message.text}
                ]
            }
        )
        result = response.json()
        reply_text = result['choices'][0]['message']['content']
        bot.reply_to(message, reply_text)
    except Exception as e:
        bot.reply_to(message, "Щось зламалося...")

print("Botkostian running...")
bot.infinity_polling()

