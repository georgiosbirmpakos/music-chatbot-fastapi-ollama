import os
import yt_dlp

def download_song_from_youtube(song_title: str):
    os.makedirs("downloads", exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'downloads/{song_title}.%(ext)s',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([f"ytsearch:{song_title}"])
            return f"{song_title}.wav downloaded"
        except Exception as e:
            return f"Error downloading {song_title}: {e}"
