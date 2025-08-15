#!./venv/bin/python3

import os

from dotenv import load_dotenv

from services import WeatherForecastService, IPGeolocationService
from db import LocationCache, WeatherDB


load_dotenv()

# API keys
API_METEO = os.getenv("API_MG")
API_IP = os.getenv("API_IP")


class WeatherApp:
    """
    Main application coordinator for weather data collection and management.

    Orchestrates the workflow between weather data retrieval, IP geocoding,
    and database operations.

    Attributes:
        weatherDB: WeatherDB
            DAO interface to interact with WeatherData database.
        weatherService: WeatherForescastService
            Interface to interact with the API of MeteoGalicia.
    """

    def __init__(self):
        self.weatherDB = WeatherDB()
        self.weatherService = WeatherForecastService(api_key=API_METEO)
        self.ipLocation = IPGeolocationService(api_key=API_IP)
        self.locationCache = LocationCache()

    def update_db(self, coords: str) -> str:
        """
        Make an API request to MeteoGal to obtain the new weather data
        for the next days and update the state of the WeatherData DB.

        Args:
            coords: str
                The longitude and latitude of the new location.

        Returns:
            str
                Weather data expire date.
        """
        wrecords = self.weatherService.get_data(coords) # Weather records

        self.weatherDB.execute_query(sql_keys=("WObservation", "Empty"))
        self.weatherDB.execute_query(sql_keys=("WObservation", "Fill"),
                                     parameters=wrecords["data"])

        return wrecords["expires_at"]

    def is_new_location(self, location_data: list) -> bool:
        """
        Use the Single IP Geolocation Lookup API from IP Geolocation to
        obtain data about your current location and compare it to
        cached data (if exists!).

        Returns:
            bool
                Check if it's a new location.
        """
        return self.locationCache.is_new_location(location_data)

    def run(self):
        """
        Main method to run the application.
        """

        # 1) Check the creation of the WeatherDB
        if not self.weatherDB.exists():
            self.weatherDB.create_db()

        # 2) Get my current location and compare with cached data
        lat, long, country, city = self.ipLocation.get_data()
        if self.is_new_location([country, city]):

            # 3) Update WeatherDB
            expires_at = self.update_db(f"{long},{lat}")

            # 4) Write the new location to the cache
            self.locationCache.save_cache(city, country, expires_at)

            print("New location was added and the DB was updated!")

if __name__ == "__main__":
    app = WeatherApp()
    app.run()
