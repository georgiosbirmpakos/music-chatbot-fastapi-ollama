# tools/download_tool.py

import os
import yt_dlp

class YouTubeDownloader:
    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def download(self, song_title: str) -> str:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.output_dir, f"{song_title}.%(ext)s"),
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
                return os.path.join(self.output_dir, f"{song_title}.wav")
            except Exception as e:
                raise RuntimeError(f"Failed to download '{song_title}': {e}")
