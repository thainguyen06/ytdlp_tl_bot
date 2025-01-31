import os
import asyncio
import subprocess
import ffmpeg
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
    """
    Extract video metadata using ffmpeg probe
    
    Args:
        file_path (str): Path to the video file
    
    Returns:
        tuple: Duration, width, height of the video (or None if not found)
    """
    try:
        probe = ffmpeg.probe(file_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream:
            duration = float(probe['format']['duration'])
            width = int(video_stream['width'])
            height = int(video_stream['height'])
            return duration, width, height
    except Exception as e:
        print(f"Error probing video: {e}")
    return None, None, None

def extract_thumbnail(video_path, thumbnail_path):
    """
    Extract a thumbnail from a video file
    
    Args:
        video_path (str): Path to the source video
        thumbnail_path (str): Path to save the thumbnail
    """
    try:
        (
            ffmpeg
            .input(video_path, ss="00:00:01")
            .filter('scale', 320, -1)
            .output(thumbnail_path, vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except Exception as e:
        print(f"Thumbnail extraction error: {e}")

def convert_media_file(input_file):
    """
    Convert media files by renaming them
    
    Args:
        input_file (str): Path to the input file
    
    Returns:
        str: Path to the converted/renamed file
    """
    # List of extensions to convert
    extensions_to_convert = {
        '.mov': '.mp4',
        '.m4v': '.mp4',
    }
    
    # Get file extension
    file_ext = os.path.splitext(input_file)[1].lower()
    
    # Check if the file needs conversion
    if file_ext in extensions_to_convert:
        # Create new file path with new extension
        output_file = os.path.splitext(input_file)[0] + extensions_to_convert[file_ext]
        
        try:
            # Rename the file
            os.rename(input_file, output_file)
            return output_file
        except Exception as e:
            print(f"File conversion error: {e}")
            return input_file
    
    return input_file

@bot.on_message(filters.command("start"))
async def start(client, message):
    """
    Handler for the /start command
    Sends a welcome message
    """
    await message.reply("こんにちは！Gửi link video YouTube để mình tải về cho bạn nhé! 🎥")

@bot.on_message(filters.text)
async def download_video(client, message):
    """
    Main handler for downloading YouTube videos
    Processes text messages with YouTube links
    """
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
        
        # Lấy thông tin video và tạo thumbnail
        duration, width, height = get_video_info(file_path)
        extract_thumbnail(file_path, thumbnail_path)
       
        try:
            # Gửi video với thông tin metadata
            await message.reply_video(
                video=file_path,
                duration=duration,
                width=width,
                height=height,
                thumb=thumbnail_path if os.path.exists(thumbnail_path) else None
            )
        except Exception as e:
            # Nếu gửi video thất bại, thử gửi lại không có metadata
            await message.reply_video(video=file_path)
       
        # Xóa các file
        if os.path.exists(thumbnail_path):
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

def main():
    """
    Main function to run the bot
    """
    print("🤖 Bot đang chạy...")
    bot.run()

if __name__ == "__main__":
    main()
