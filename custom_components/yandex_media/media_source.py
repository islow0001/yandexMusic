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

from .yandex_client import YandexClient

_LOGGER = logging.getLogger(__name__)

async def async_get_media_source(hass: HomeAssistant):
    """Set up Yandex Media source."""
    _LOGGER.error("===== YANDEX MEDIA: async_get_media_source CALLED =====")
    return YandexMediaSource(hass)

class YandexMediaSource(MediaSource):
    """Yandex Music media source."""

    def __init__(self, hass: HomeAssistant):
        super().__init__("yandex_media")
        self.hass = hass
        self.name = "Yandex Media"
        self.client = YandexClient()

    async def async_browse_media(self, item: MediaSourceItem):
        """Browse media."""
        _LOGGER.error(f"===== YANDEX MEDIA: browse_media: {item.identifier} =====")

        # Корень
        if item.identifier is None or item.identifier == "":
            children = []
            
            # Добавляем все треки из клиента
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
                identifier=None,
                media_class=MediaClass.DIRECTORY,
                media_content_type="",
                children_media_class=MediaClass.TRACK,
                title="Yandex Music (Demo)",
                can_play=False,
                can_expand=True,
                children=children,
            )

        # Если выбран трек
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
        """Resolve media."""
        _LOGGER.error(f"===== YANDEX MEDIA: resolve_media: {item.identifier} =====")
        
        if item.identifier and item.identifier.startswith("track_"):
            track_id = item.identifier.replace("track_", "")
            track = self.client.get_track(track_id)
            
            if track:
                return PlayMedia(
                    url=track["url"],
                    mime_type="audio/mpeg",
                )
        
        raise Unresolvable("Unknown item")