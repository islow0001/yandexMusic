DOMAIN = "yandex_media"

async def async_setup(hass, config):
    hass.data[DOMAIN] = {}
    return True