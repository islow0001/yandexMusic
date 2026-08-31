import logging
import base64
from homeassistant.components.media_source import (
    BrowseMediaSource,
    MediaSource,
    MediaSourceItem,
    PlayMedia,
    Unresolvable,
)
from homeassistant.core import HomeAssistant
from homeassistant.components.media_player import MediaClass, MediaType

from .yandex_client import YandexClient

_LOGGER = logging.getLogger(__name__)

async def async_get_media_source(hass: HomeAssistant):
    _LOGGER.error("===== YANDEX MEDIA: async_get_media_source CALLED =====")
    return YandexMediaSource(hass)


class YandexMediaSource(MediaSource):
    def __init__(self, hass: HomeAssistant):
        super().__init__("yandex_media")
        self.hass = hass
        self.name = "Yandex Media"
        self.client = YandexClient()

    async def async_browse_media(self, item: MediaSourceItem):
        _LOGGER.error(f"===== YANDEX MEDIA: browse_media: {item.identifier} =====")

        # Корень
        if item.identifier is None or item.identifier == "":
            children = []
            for track in self.client.get_tracks():
                children.append(
                    BrowseMediaSource(
                        domain=self.domain,
                        identifier=f"track_{track['id']}",
                        media_class=MediaClass.TRACK,
                        media_content_type=MediaType.MUSIC,
                        title=f"{track['artist']} - {track['title']}",
                        can_play=True,
                        can_expand=False,
                        thumbnail=track.get("thumbnail"),
                    )
                )

            return BrowseMediaSource(
                domain=self.domain,
                identifier="playlist_all",
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                children_media_class=MediaClass.TRACK,
                title="Yandex Music",
                can_play=True,
                can_expand=True,
                children=children,
            )

        # Если выбрали весь плейлист (воспроизвести всё)
        if item.identifier == "playlist_all":
            return PlayMedia(
                url="yandex_media://playlist_all",
                mime_type="audio/mpegurl",
            )

        # Если выбран отдельный трек
        if item.identifier and item.identifier.startswith("track_"):
            track_id = item.identifier.replace("track_", "")
            track = self.client.get_track(track_id)
            if track:
                return PlayMedia(
                    url=track["url"],
                    mime_type="audio/mpeg",
                )

        return None

    async def async_resolve_media(self, item: MediaSourceItem):
        _LOGGER.error(f"===== YANDEX MEDIA: resolve_media: {item.identifier} =====")
        
        # Это наш флаг, что нужно создать плейлист
        if item.identifier == "playlist_all":
            tracks = self.client.get_tracks()
            
            # Создаем M3U плейлист
            m3u = "#EXTM3U\n"
            for track in tracks:
                m3u += f"#EXTINF:{track.get('duration', -1)},{track['artist']} - {track['title']}\n"
                m3u += f"{track['url']}\n"
            
            m3u_b64 = base64.b64encode(m3u.encode()).decode()
            return PlayMedia(
                url=f"data:audio/mpegurl;base64,{m3u_b64}",
                mime_type="audio/mpegurl",
            )
        
        # Отдельный трек
        if item.identifier and item.identifier.startswith("track_"):
            track_id = item.identifier.replace("track_", "")
            track = self.client.get_track(track_id)
            if track:
                return PlayMedia(
                    url=track["url"],
                    mime_type="audio/mpeg",
                )
        
        raise Unresolvable("Unknown item")