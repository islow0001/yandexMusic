import os
import requests

CACHE_DIR = "/media/local/yandex_cache/"

class YandexClient:
    def __init__(self):
        self._tracks_cache = None
        # тут твоя авторизация

    def get_loved_tracks(self):
        """Возвращает список словарей с id, title, artist"""
        # Твой код, который парсит плейлист
        # Возвращай типа:
        return [
            {"id": "123", "title": "Track1", "artist": "Artist1"},
            {"id": "456", "title": "Track2", "artist": "Artist2"},
        ]

    def download_track(self, track_id):
        """Скачивает mp3 и возвращает путь к файлу"""
        os.makedirs(CACHE_DIR, exist_ok=True)
        filepath = os.path.join(CACHE_DIR, f"{track_id}.mp3")
        
        if os.path.exists(filepath):
            return filepath  # уже скачан
        
        # Твой код скачивания
        url = f"https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"  # получаешь ссылку на mp3
        response = requests.get(url)
        with open(filepath, "wb") as f:
            f.write(response.content)
        
        return filepath