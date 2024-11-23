apt update && apt upgrade -y
apt install ffmpeg python3-venv -y
python3 -m venv venv
. venv/bin/activate
pip install -r re.txt
python3 bot.py
