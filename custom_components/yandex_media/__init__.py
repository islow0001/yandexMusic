import logging
from homeassistant.core import HomeAssistant
import voluptuous as vol
from homeassistant.const import CONF_ENTITY_ID

DOMAIN = "yandex_media"
_LOGGER = logging.getLogger(__name__)

SERVICE_PLAY_PLAYLIST = "play_playlist"

SERVICE_SCHEMA = vol.Schema({
    vol.Required("entity_id"): str,
    vol.Optional("shuffle", default=False): bool,
})

async def async_setup(hass: HomeAssistant, config: dict):
    _LOGGER.error("===== YANDEX MEDIA: LOADED =====")
    hass.data[DOMAIN] = {}
    
    from .yandex_client import YandexClient
    
    async def handle_play_playlist(call):
        entity_id = call.data["entity_id"]
        shuffle = call.data.get("shuffle", False)
        client = YandexClient()
        tracks = client.get_tracks()
        
        if shuffle:
            import random
            shuffled = tracks.copy()
            random.shuffle(shuffled)
            tracks = shuffled
        
        # Первый трек — воспроизводим с заменой очереди
        first_track = tracks[0]
        await hass.services.async_call(
            "media_player",
            "play_media",
            {
                "entity_id": entity_id,
                "media_content_id": first_track["url"],
                "media_content_type": "audio/mpeg",
                "enqueue": "replace",
            }
        )
        
        # Остальные треки — добавляем в очередь
        for track in tracks[1:]:
            await hass.services.async_call(
                "media_player",
                "play_media",
                {
                    "entity_id": entity_id,
                    "media_content_id": track["url"],
                    "media_content_type": "audio/mpeg",
                    "enqueue": "play",
                }
            )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_PLAY_PLAYLIST,
        handle_play_playlist,
        schema=SERVICE_SCHEMA
    )
    
    return True