import logging
from homeassistant.core import HomeAssistant
import voluptuous as vol

DOMAIN = "yandex_media"
_LOGGER = logging.getLogger(__name__)

CONF_TOKEN = "token"

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_TOKEN): str,
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up Yandex Media integration."""
    _LOGGER.error("===== YANDEX MEDIA: LOADED =====")
    
    # Сохраняем токен
    if DOMAIN in config:
        hass.data[DOMAIN] = {
            'token': config[DOMAIN].get(CONF_TOKEN)
        }
    else:
        hass.data[DOMAIN] = {}
    
    return True