from backend.tools.youtube_downloader import YouTubeDownloader, SongItem

def test_download_batch_monkeypatch(monkeypatch, tmp_path):
    yd = YouTubeDownloader()
    # prevent actual downloads
    def fake_download(q): return str(tmp_path / (q.replace(" ", "_") + ".mp3"))
    monkeypatch.setattr(yd, "download", fake_download)

    items = [SongItem(title="Billie Jean", artist="Michael Jackson")]
    res = yd.download_batch(items)
    assert res[0].status == "ok"
    assert res[0].path.endswith(".mp3")
