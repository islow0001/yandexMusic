import logging
from homeassistant.components.media_source import (
    BrowseMediaSource,
    MediaSource,
    MediaSourceItem,
    PlayMedia,
    Unresolvable,
)
from homeassistant.core import HomeAssistant
from homeassistant.components.media_player import MediaClass, MediaType
from homeassistant.helpers import config_validation as cv

from .yandex_client import YandexClient

_LOGGER = logging.getLogger(__name__)

DOMAIN = "yandex_media"

async def async_get_media_source(hass: HomeAssistant):
    return YandexMediaSource(hass)

class YandexMediaSource(MediaSource):
    def __init__(self, hass: HomeAssistant):
        super().__init__(DOMAIN)
        self.hass = hass
        self.name = "Yandex Music"
        self.client = None
        self._playlists = []

    async def async_initialize(self):
        """Инициализация клиента с токеном из config."""
        if self.client:
            return
            
        # Получаем токен из конфига
        token = self.hass.data[DOMAIN].get('token')
        if not token:
            _LOGGER.error("===== YANDEX MEDIA: NO TOKEN IN CONFIG =====")
            return
            
        self.client = YandexClient(token=token)
        await self.hass.async_add_executor_job(self.client.auth)
        
        # Получаем список плейлистов
        self._playlists = await self.hass.async_add_executor_job(self.client.get_playlists)

    async def async_browse_media(self, item: MediaSourceItem):
        """Browse media."""
        await self.async_initialize()
        
        if not self.client or not self.client.client:
            _LOGGER.error("===== YANDEX MEDIA: CLIENT NOT AUTHED =====")
            return BrowseMediaSource(
                domain=self.domain,
                identifier=None,
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                title="Yandex Music (ошибка авторизации)",
                can_play=False,
                can_expand=False,
            )

        _LOGGER.error(f"===== YANDEX MEDIA: browse_media: {item.identifier} =====")

        # Корень — показываем список плейлистов
        if item.identifier is None or item.identifier == "":
            children = []
            
            for pl in self._playlists:
                children.append(
                    BrowseMediaSource(
                        domain=self.domain,
                        identifier=f"playlist_{pl['id']}",
                        media_class=MediaClass.DIRECTORY,
                        media_content_type="",
                        title=pl['title'],
                        can_play=False,
                        can_expand=True,
                    )
                )

            return BrowseMediaSource(
                domain=self.domain,
                identifier=None,
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                children_media_class=MediaClass.DIRECTORY,
                title="Yandex Music",
                can_play=False,
                can_expand=True,
                children=children,
            )

        # Выбран плейлист
        if item.identifier and item.identifier.startswith("playlist_"):
            playlist_id = int(item.identifier.replace("playlist_", ""))
            
            _LOGGER.error(f"===== YANDEX MEDIA: loading playlist {playlist_id} =====")
            
            # Получаем треки плейлиста
            tracks = await self.hass.async_add_executor_job(
                self.client.get_playlist_tracks, playlist_id
            )
            
            children = []
            for track in tracks:
                children.append(
                    BrowseMediaSource(
                        domain=self.domain,
                        identifier=f"track_{track['id']}",
                        media_class=MediaClass.TRACK,
                        media_content_type=MediaType.MUSIC,
                        title=f"{track['artist']} - {track['title']}",
                        can_play=True,
                        can_expand=False,
                        thumbnail=track.get('thumbnail'),
                    )
                )

            return BrowseMediaSource(
                domain=self.domain,
                identifier=item.identifier,
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                children_media_class=MediaClass.TRACK,
                title="Треки",
                can_play=False,
                can_expand=True,
                children=children,
            )

        # Выбран трек
        if item.identifier and item.identifier.startswith("track_"):
            track_id = int(item.identifier.replace("track_", ""))
            
            # Скачиваем трек
            path = await self.hass.async_add_executor_job(
                self.client.download_track, track_id
            )
            
            if path:
                # Отдаем локальный URL
                url = f"/local/yandex_cache/{os.path.basename(path)}"
                return PlayMedia(
                    url=url,
                    mime_type="audio/mpeg",
                )

        return None

    async def async_resolve_media(self, item: MediaSourceItem):
        """Resolve media."""
        await self.async_initialize()
        
        _LOGGER.error(f"===== YANDEX MEDIA: resolve_media: {item.identifier} =====")
        
        if item.identifier and item.identifier.startswith("track_"):
            track_id = int(item.identifier.replace("track_", ""))
            
            path = await self.hass.async_add_executor_job(
                self.client.download_track, track_id
            )
            
            if path:
                url = f"/local/yandex_cache/{os.path.basename(path)}"
                return PlayMedia(
                    url=url,
                    mime_type="audio/mpeg",
                )
        
        raise Unresolvable("Unknown item")