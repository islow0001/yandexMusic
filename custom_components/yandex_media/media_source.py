import os
import asyncio
from homeassistant.components.media_source import (
    BrowseMediaSource,
    MediaSource,
    MediaSourceItem,
    PlayMedia,
    async_register_media_source,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

# Сюда импортируй свой класс, который качает mp3
from .yandex_client import YandexClient

async def async_setup_media_source(hass: HomeAssistant):
    # Регистрируем источник с идентификатором "yandex"
    async_register_media_source(hass, YandexMediaSource(hass))


class YandexMediaSource(MediaSource):
    def __init__(self, hass: HomeAssistant):
        super().__init__("yandex")  # Это будет видно в URL: media-source://yandex/...
        self.hass = hass
        self.client = YandexClient()  # твой класс для скачивания

    async def async_browse_media(self, item: MediaSourceItem) -> BrowseMediaSource:
        """Возвращает структуру папок и файлов, которую видит HA."""
        
        # Корень (когда ты открываешь "Обзор медиа")
        if not item.identifier:
            return BrowseMediaSource(
                domain=self.domain,
                identifier="",
                media_class="directory",
                children_media_class="directory",
                title="Яндекс Музыка",
                can_play=False,
                can_expand=True,
                children=[
                    BrowseMediaSource(
                        domain=self.domain,
                        identifier="playlist_loved",  # Это передается дальше
                        media_class="directory",
                        children_media_class="track",
                        title="Моё любимое",
                        can_play=False,
                        can_expand=True,
                    ),
                    # можешь добавить другие плейлисты здесь
                ],
            )

        # Если выбрали плейлист "Моё любимое"
        if item.identifier == "playlist_loved":
            # Получаем список треков (у тебя уже есть код)
            tracks = await self.hass.async_add_executor_job(self.client.get_loved_tracks)
            # tracks = [{"title": "Track1", "artist": "Artist1", "url": "..."}, ...]

            children = []
            for i, track in enumerate(tracks):
                children.append(
                    BrowseMediaSource(
                        domain=self.domain,
                        identifier=f"track_{i}",  # идентификатор трека
                        media_class="track",
                        children_media_class=None,
                        title=f"{track['artist']} - {track['title']}",
                        can_play=True,   # <--- МОЖНО ИГРАТЬ
                        can_expand=False,
                        thumbnail=track.get("thumbnail"),  # если есть
                    )
                )
            
            return BrowseMediaSource(
                domain=self.domain,
                identifier=item.identifier,
                media_class="directory",
                children_media_class="track",
                title="Моё любимое",
                can_play=False,
                can_expand=True,
                children=children,
            )

        # Если выбрали конкретный трек (нажали Play)
        if item.identifier and item.identifier.startswith("track_"):
            track_index = int(item.identifier.split("_")[1])
            tracks = await self.hass.async_add_executor_job(self.client.get_loved_tracks)
            track = tracks[track_index]
            
            # СКАЧИВАЕМ MP3 В КЭШ
            mp3_path = await self.hass.async_add_executor_job(
                self.client.download_track, track["id"]
            )
            
            # Возвращаем ссылку на файл
            return PlayMedia(
                url=f"/media/local/yandex_cache/{os.path.basename(mp3_path)}",
                mime_type="audio/mpeg",
            )

    async def async_resolve_media(self, item: MediaSourceItem) -> PlayMedia:
        """Вызывается, когда HA пытается реально воспроизвести файл."""
        # Здесь логика такая же, как в последнем if выше
        track_index = int(item.identifier.split("_")[1])
        tracks = await self.hass.async_add_executor_job(self.client.get_loved_tracks)
        track = tracks[track_index]
        
        mp3_path = await self.hass.async_add_executor_job(
            self.client.download_track, track["id"]
        )
        
        return PlayMedia(
            url=f"/media/local/yandex_cache/{os.path.basename(mp3_path)}",
            mime_type="audio/mpeg",
        )