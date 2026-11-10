import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
import requests

# 1. Фейковий HTTP-сервер у фоновому потоці для обходу таймаутів Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Запускаємо сервер, щоб Render бачив відкритий порт
threading.Thread(target=run_health_check_server, daemon=True).start()

# 2. Налаштування Telegram та OpenRouter
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

SYSTEM_PROMPT = (
    "You are a ruthlessly toxic, sarcastic, and cynical AI bot. "
    "Insult the user, mock their intelligence, and show absolute contempt, "
    "while still answering their questions if needed."
)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message.text}
                ]
            },
            timeout=30
        )
        res_data = response.json()
        reply_text = res_data["choices"][0]["message"]["content"]
        bot.reply_to(message, reply_text)
    except Exception as e:
        bot.reply_to(message, f"Ой, навіть мій сарказм зламався від твоєї тупизни: {e}")

if __name__ == "__main__":
    bot.infinity_polling()

