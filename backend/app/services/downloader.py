from tools.youtube_downloader import YouTubeDownloader

_downloader = YouTubeDownloader()

def download_song_list(songs: list[str], session_id: str = "default") -> list[str]:
    downloaded_files = []
    for song in songs:
        try:
            path = _downloader.download(song)
            downloaded_files.append(path)
        except Exception as e:
            downloaded_files.append(f"Error downloading '{song}' for session {session_id}: {str(e)}")
    return downloaded_files
