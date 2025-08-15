import os
from datetime import datetime

import json


class LocationCache:
    """
    File-based location caching with conditional TTL updates.

    Stores current location (city, country) in a JSON file and only updates
    the cache and resets the TTL when the location actually changes, or when
    the cache expires.
    """

    def __init__(self, cache_file: str = "current_location.json"):
        self.cache_file = cache_file

    def load_cache(self) -> dict | None:
        """
        Load existing cache data from file.

        Returns:
            dict | None
                None if file doesn't exist or is invalid.
        """
        if not os.path.exists(self.cache_file):
            return None

        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
                return cache_data
        except (json.JSONDecodeError, IOError):
            return None

        return None

    def _is_cache_valid(self) -> bool:
        """
        Check if cached data is still within TTL period.

        """
        cached_data = self.load_cache()

        expires_at = datetime.fromisoformat(cached_data['expires_at'])
        return datetime.now() < expires_at

    def is_new_location(self, new_location:list[str, str]) -> bool:
        """
        Check if the location data (country, city) has changed.

        Args:
            new_location: list[str, str]
                Location obtained from ipgeolocation API.
        Returns
            bool
                Indicate if the location has changed.
        """
        current_city, current_country = new_location
        cached_data = self.load_cache()

        if cached_data is None:
            return True
            T
        cached_city, cached_country = [cached_data[k] for k in ["city", "country"]]
        has_changed = (current_city != cached_city or
                          current_country != cached_country)

        if has_changed or not self._is_cache_valid():
            return True

        return False

    def save_cache(self, city: str, country: str, expires_at: int):
            """
            Save location data with TTL to cache file.

            Args:
                city: str
                    New city
                country: str
                    New country
                expires_at: int
                    When the data expires at.
            """
            cache_data = {
                'city': city,
                'country': country,
                'expires_at': expires_at,
                'last_updated': datetime.now().isoformat()
            }

            try:
                with open(self.cache_file, 'w') as f:
                    json.dump(cache_data, f, indent=2)
            except IOError as e:
                raise e
