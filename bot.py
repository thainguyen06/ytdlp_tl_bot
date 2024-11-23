import os
import asyncio
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

# Thông tin bot
API_ID = 6897064  # Thay bằng API ID của bạn
API_HASH = "206c2035a8dc342ab70421ea4094ac49"  # Thay bằng API Hash của bạn
BOT_TOKEN = "7377403730:AAFCfrrbxfCAJ_ylHnHgPeUIepJKB1wwtSA"  # Thay bằng Token bot của bạn

# Khởi tạo bot
bot = Client("yt_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Cấu hình yt-dlp
ydl_opts = {
    "outtmpl": "downloads/%(title)s.%(ext)s",
    "format": "bestvideo+bestaudio/best",
}

# Tạo thư mục tải xuống
if not os.path.exists("downloads"):
    os.makedirs("downloads")


@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("こんにちは！Gửi link video YouTube để mình tải về cho bạn nhé! 🎥")


@bot.on_message(filters.text & ~filters.command)
async def download_video(client, message):
    url = message.text.strip()
    await message.reply("⏳ Đang tải video...")

    try:
        # Tải video với yt-dlp
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        
        # Upload video lên Telegram
        await message.reply_video(video=file_path, caption=f"🎬 Video: {info['title']}")
        
        # Xóa file sau khi upload
        os.remove(file_path)
    except Exception as e:
        await message.reply(f"⚠️ Lỗi: {str(e)}")


if __name__ == "__main__":
    print("Bot đang chạy...")
    bot.run()
