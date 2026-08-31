import logging

_LOGGER = logging.getLogger(__name__)


class YandexClient:
    """Demo client with 3 test tracks."""

    def __init__(self):
        self._tracks = [
            {
                "id": "1",
                "title": "SoundHelix Song 1",
                "artist": "SoundHelix",
                "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                "thumbnail": "https://www.soundhelix.com/examples/mp3/logo.png",
                "duration": 20,
            },
            {
                "id": "2",
                "title": "SoundHelix Song 2",
                "artist": "SoundHelix",
                "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
                "thumbnail": "https://www.soundhelix.com/examples/mp3/logo.png",
                "duration": 20,
            },
            {
                "id": "3",
                "title": "SoundHelix Song 3",
                "artist": "SoundHelix",
                "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
                "thumbnail": "https://www.soundhelix.com/examples/mp3/logo.png",
                "duration": 20,
            },
        ]

    def get_tracks(self):
        """Return list of tracks."""
        _LOGGER.error(f"===== YANDEX CLIENT: returning {len(self._tracks)} tracks =====")
        return self._tracks

    def get_track(self, track_id):
        """Return track by ID."""
        for track in self._tracks:
            if track["id"] == track_id:
                return track
        return None