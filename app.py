from hazm import word_tokenize, Normalizer, stopwords_list
from flask import Flask, request
import requests
import re
import os

app = Flask(__name__)

# دریافت توکن و URL API از متغیرهای محیطی
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = os.getenv("TELEGRAM_API_URL") + TOKEN

# ابزارهای پردازش متن فارسی
normalizer = Normalizer()
stopwords = set(stopwords_list())  # استفاده از stopwords_list

def generate_slug(text):
    """تبدیل متن به نامک (Slug)"""
    text = normalizer.normalize(text)  
    text = re.sub(r"[^\w\s-]", "", text)  
    text = text.replace(" ", "-")  
    return text.lower()

def extract_keywords(text):
    """استخراج کلمات کلیدی"""
    words = word_tokenize(normalizer.normalize(text))
    keywords = [word for word in words if word not in stopwords and len(word) > 2]
    return ", ".join(keywords[:10])

@app.route('/')
def home():
    return "ربات پردازش متن فارسی فعال است!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """دریافت پیام از تلگرام و پردازش آن"""
    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        slug = generate_slug(text)
        keywords = extract_keywords(text)

        response_text = f"📌 **نامک:** `{slug}`\n🔑 **کلمات کلیدی:** `{keywords}`"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", data={"chat_id": chat_id, "text": response_text, "parse_mode": "Markdown"})

    return '', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
