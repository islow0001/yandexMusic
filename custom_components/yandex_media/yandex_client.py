import os
import logging
import pygame
from pygame import mixer
from yandex_music import Client

_LOGGER = logging.getLogger(__name__)

class YandexClient:
    """Клиент для Яндекс Музыки."""

    def __init__(self, token=None):
        _LOGGER.error("===== YANDEX CLIENT: INIT =====")
        
        self.token = token
        self.client = None
        self.download_dir = "/config/www/yandex_cache"
        self.current_track_index = None
        self.is_playing = False
        self.tracks_per_page = 20
        self.current_page = 0
        self.all_tracks = []
        self.loaded_tracks = []
        
        # Инициализация
        pygame.init()
        mixer.init()
        os.makedirs(self.download_dir, exist_ok=True)

    def auth(self):
        """Авторизация с токеном."""
        if not self.token:
            _LOGGER.error("===== YANDEX CLIENT: NO TOKEN =====")
            return False
            
        try:
            self.client = Client(self.token).init()
            _LOGGER.error("===== YANDEX CLIENT: AUTH SUCCESS =====")
            return True
        except Exception as e:
            _LOGGER.error(f"Yandex Client auth error: {e}")
            return False

    def get_playlists(self):
        """Возвращает список доступных плейлистов."""
        if not self.client:
            return []
            
        playlists = [
            {"id": -1, "title": "Моё любимое"},
            {"id": -2, "title": "Плейлист дня"}
        ]
        
        # Добавляем пользовательские плейлисты
        try:
            user_playlists = self.client.users_playlists_list()
            for pl in user_playlists:
                playlists.append({"id": pl.kind, "title": pl.title})
        except:
            pass
            
        return playlists

    def select_playlist(self, index):
        """Выбор плейлиста."""
        _LOGGER.error(f"===== YANDEX CLIENT: select_playlist {index} =====")
        
        if not self.client:
            _LOGGER.error("===== YANDEX CLIENT: NOT AUTHED =====")
            return []
            
        self.all_tracks = []
        self.loaded_tracks = []
        self.current_page = 0
        self.current_track_index = None

        try:
            if index == -1:
                _LOGGER.error("Загружаем любимые песни...")
                liked = [i.fetch_track() for i in self.client.users_likes_tracks()]
                self.all_tracks = liked
                
            elif index == -2:
                _LOGGER.error("Загружаем плейлист дня...")
                PersonalPlaylistBlocks = self.client.landing(blocks=['personalplaylists']).blocks[0]
                DailyPlaylist = next(
                    x.data.data for x in PersonalPlaylistBlocks.entities 
                    if x.data.data.generated_playlist_type == 'playlistOfTheDay'
                )
                playlist = self.client.users_playlists(DailyPlaylist.kind, user_id=DailyPlaylist.uid)
                self.all_tracks = playlist.tracks
            else:
                _LOGGER.error(f"Загружаем плейлист {index}...")
                playlist = self.client.users_playlists(index)
                self.all_tracks = playlist.tracks
                
            _LOGGER.error(f"Всего треков: {len(self.all_tracks)}")
            self._load_more_tracks()
            
        except Exception as e:
            _LOGGER.error(f"Ошибка при загрузке плейлиста: {e}")
            
        return self.loaded_tracks

    def _load_more_tracks(self):
        """Загрузка следующей порции треков."""
        try:
            start_idx = self.current_page * self.tracks_per_page
            end_idx = start_idx + self.tracks_per_page
            
            new_tracks = self.all_tracks[start_idx:end_idx]
            
            for item in new_tracks:
                if isinstance(item, str):
                    continue
                if hasattr(item, 'track'):
                    track = item.track
                else:
                    track = item
                    
                self.loaded_tracks.append({
                    'id': len(self.loaded_tracks),
                    'track': track,
                    'path': None
                })
            
            self.current_page += 1
            _LOGGER.error(f"Загружено {len(new_tracks)} треков. Всего: {len(self.loaded_tracks)}")
            
        except Exception as e:
            _LOGGER.error(f"Ошибка загрузки треков: {e}")

    def download_track(self, track_id):
        """Скачивает трек и возвращает путь."""
        try:
            if track_id >= len(self.loaded_tracks):
                return None
                
            track_data = self.loaded_tracks[track_id]
            if track_data['path'] and os.path.exists(track_data['path']):
                return track_data['path']
                
            track = track_data['track']
            filename = f"{track_data['id']}.mp3"
            path = os.path.join(self.download_dir, filename)
            
            _LOGGER.error(f"Скачиваем трек: {filename}")
            track.download(path)
            self.loaded_tracks[track_id]['path'] = path
            return path
            
        except Exception as e:
            _LOGGER.error(f"Ошибка скачивания: {e}")
            return None

    def get_playlist_tracks(self, playlist_id):
        """Получает список треков для плейлиста в формате для HA."""
        tracks_data = self.select_playlist(playlist_id)
        
        # Форматируем для HA
        result = []
        for item in tracks_data:
            track = item['track']
            # Пытаемся получить название
            title = getattr(track, 'title', 'Неизвестно')
            artists = getattr(track, 'artists', [])
            artist = artists[0].name if artists else 'Неизвестен'
            
            # Получаем обложку
            cover = None
            if hasattr(track, 'cover') and track.cover:
                cover = track.cover.uri
                
            result.append({
                'id': str(item['id']),
                'title': title,
                'artist': artist,
                'thumbnail': cover,
                'duration': 30,  # Демо, можно получить реальную длительность
            })
            
        return result

    def play_track(self, track_id):
        """Воспроизводит трек (опционально)."""
        path = self.download_track(track_id)
        if path:
            mixer.music.load(path)
            mixer.music.play()
            return True
        return False