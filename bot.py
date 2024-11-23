import os
import asyncio
import subprocess
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

# Thông tin bot
API_ID = id
API_HASH = "hash"
BOT_TOKEN = "token"

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

def get_video_info(file_path):
   try:
       cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
              '-show_entries', 'stream=width,height,duration',
              '-of', 'json', file_path]
       
       result = subprocess.run(cmd, capture_output=True, text=True)
       if result.returncode == 0:
           output = eval(result.stdout)
           stream = output.get('streams', [{}])[0]
           width = int(stream.get('width', 0))
           height = int(stream.get('height', 0))
           duration = int(float(stream.get('duration', 0)))
           return duration, width, height
   except:
       pass
   return None, None, None

def create_thumbnail(video_path, thumbnail_path):
   try:
       cmd = ['ffmpeg', '-i', video_path, '-ss', '00:00:01.000', 
              '-vframes', '1', thumbnail_path, '-y']
       subprocess.run(cmd, capture_output=True)
       # Kiểm tra xem file thumbnail có tồn tại không
       if os.path.exists(thumbnail_path):
           return True
   except:
       pass
   return False

@bot.on_message(filters.command("start"))
async def start(client, message):
   await message.reply("こんにちは！Gửi link video YouTube để mình tải về cho bạn nhé! 🎥")

@bot.on_message(filters.text)
async def download_video(client, message):
   if message.text.startswith("/"):
       return
       
   url = message.text.strip()

   try:
       # Gửi tin nhắn đầu tiên và lưu vào biến status_msg
       status_msg = await message.reply("⏳ **Đang xử lý video...**")
       
       # Cập nhật trạng thái đang tải xuống
       await status_msg.edit("📥 **Đang tải xuống video...**")
       
       # Tải video với yt-dlp
       with YoutubeDL(ydl_opts) as ydl:
           info = ydl.extract_info(url, download=True)
           file_path = ydl.prepare_filename(info)
       
       # Kiểm tra xem file có tồn tại không
       if not os.path.exists(file_path):
           raise Exception("Video không tải được")
           
       # Cập nhật trạng thái đang upload
       await status_msg.edit("📤 **Đang tải video lên Telegram...**")

       # Tạo thumbnail trong cùng thư mục với video
       thumbnail_path = os.path.join(os.path.dirname(file_path), f"{os.path.basename(file_path)}_thumb.jpg")
       duration, width, height = get_video_info(file_path)
       thumbnail_created = create_thumbnail(file_path, thumbnail_path)
       
       try:
           # Gửi video với thông tin metadata
           await message.reply_video(
               video=file_path,
               duration=duration,
               width=width,
               height=height,
               thumb=thumbnail_path if thumbnail_created and os.path.exists(thumbnail_path) else None
           )
       except Exception as e:
           # Nếu gửi video thất bại, thử gửi lại không có metadata
           await message.reply_video(video=file_path)
       
       # Xóa các file
       if thumbnail_created and os.path.exists(thumbnail_path):
           try:
               os.remove(thumbnail_path)
           except:
               pass
               
       if os.path.exists(file_path):
           try:
               os.remove(file_path)
           except:
               pass
       
       # Xóa message trạng thái
       await status_msg.delete()
       
   except Exception as e:
       # Nếu có status_msg (đã tạo) thì mới edit
       if 'status_msg' in locals():
           await status_msg.edit(f"⚠️ **Lỗi:** {str(e)}")
       else:
           # Nếu lỗi xảy ra trước khi tạo status_msg
           await message.reply(f"⚠️ **Lỗi:** {str(e)}")

print("🤖 Bot đang chạy...")
bot.run()
