import os
import requests
import cv2
import numpy as np
from PIL import Image
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import yt_dlp

BOT_TOKEN = os.getenv("BOT_TOKEN")

def get_tiktok_images(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        images = []
        if 'entries' in info:
            for entry in info['entries']:
                if 'url' in entry:
                    images.append(entry['url'])
        elif 'url' in info:
            images.append(info['url'])
        return images

def images_to_video(image_urls, output_path="output.mp4"):
    frames = []
    for img_url in image_urls:
        r = requests.get(img_url, timeout=10)
        arr = np.frombuffer(r.content, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is not None:
            img = cv2.resize(img, (720, 1280))
            for _ in range(48):
                frames.append(img)

    if not frames:
        return None

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), 24, (720, 1280))
    for f in frames:
        out.write(f)
    out.release()
    return output_path

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    await update.message.reply_text("⏳ جاري التحويل...")

    try:
        images = get_tiktok_images(url)
        if not images:
            await update.message.reply_text("❌ مش قادر أجيب الصور")
            return

        video_path = images_to_video(images)
        if not video_path:
            await update.message.reply_text("❌ فشل عمل الفيديو")
            return

        await update.message.reply_video(video=open(video_path, 'rb'))

    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()
