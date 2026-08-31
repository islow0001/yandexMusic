import logging
from homeassistant.core import HomeAssistant

DOMAIN = "yandex_media"
_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up Yandex Media integration."""
    _LOGGER.error("===== YANDEX MEDIA: LOADED =====")
    hass.data[DOMAIN] = {}
    return True