import os
import re
import yt_dlp
from pathlib import Path
class YouTubeDownloader:
    def __init__(self):
        self.download_folder = Path.home() / "Downloads"
        self.download_folder.mkdir(exist_ok=True)

    def sanitize_filename(self, name: str) -> str:
        """
        Removes illegal characters for Windows and replaces them with underscores.
        Also replaces en-dash with a normal hyphen.
        """
        safe_name = re.sub(r'[<>:"/\\|?*]', "_", name)
        return safe_name.replace("–", "-")

    def download(self, song_name: str) -> str:
        """
        Search YouTube for the song and download the best audio as .mp3.
        Returns the path to the downloaded file.
        """
        safe_name = self.sanitize_filename(song_name)
        output_template = os.path.join(self.download_folder, f"{safe_name}.%(ext)s")

        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "default_search": "ytsearch1",
            "outtmpl": output_template,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song_name, download=True)
            filename = ydl.prepare_filename(info)
            final_filename = os.path.splitext(filename)[0] + ".mp3"
            return final_filename
