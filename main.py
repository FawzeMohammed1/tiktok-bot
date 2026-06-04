import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
from moviepy.editor import ImageClip, concatenate_videoclips

BOT_TOKEN = os.getenv("BOT_TOKEN")

def get_images(url):
    # مؤقتًا (هنعدلها بعدين لاستخراج تيك توك)
    return []

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    images = get_images(url)

    if not images:
        await update.message.reply_text("مش قادر أجيب الصور من اللينك دلوقتي.")
        return

    paths = []
    for i, img in enumerate(images):
        path = f"{i}.jpg"
        r = requests.get(img)
        open(path, "wb").write(r.content)
        paths.append(path)

    clips = [ImageClip(p).set_duration(2) for p in paths]
    video = concatenate_videoclips(clips)

    out = "out.mp4"
    video.write_videofile(out, fps=24)

    await update.message.reply_video(video=open(out, "rb"))

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, handle))
app.run_polling()
