from chains.mood_to_songs_chain import MoodToSongsChain
from tools.youtube_downloader import YouTubeDownloader

class MusicService:
    def __init__(self, chain: MoodToSongsChain, downloader: YouTubeDownloader):
        self.chain = chain
        self.downloader = downloader

    def recommend_and_download(self, mood: str) -> list[str]:
        songs = self.chain.get_songs(mood)
        downloaded_files = []
        for song in songs:
            try:
                path = self.downloader.download(song)
                downloaded_files.append(path)
            except Exception as e:
                downloaded_files.append(f"Error downloading '{song}': {str(e)}")
        return downloaded_files
