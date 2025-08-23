#!./venv/bin/python3

from datetime import datetime, time
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

    def needs_update(self, location_data: list) -> bool:
        """
        Use the Single IP Geolocation Lookup API from IP Geolocation to
        obtain data about your current location and compare it to
        cached data (if exists!). Then, if the location has not changed,
        it chekcs if the data is valid or not to perform an update.

        Returns:
            bool
                Check if it's a new location.
        """
        return (self.locationCache.is_new_location(location_data) or
                not self.locationCache.is_cache_valid())

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
        self.weatherDB.insert_wobservations(data=wrecords["data"])

        return wrecords["expires_at"]

    def update_wdata(self):
        """
        Get the weather data for the current hour, and write it into a
        file that can be read from the Polybar config file.
        """
        # 1) Get my current datetime.
        now = datetime.now()
        date_part = now.date().strftime("%Y-%m-%d")
        time_part = time(now.hour, 0, 0).strftime("%H:%M:%S")

        # 2) Use them to retrieve the weather data.
        db = WeatherDB()
        wdata: list[tuple[int]] = db.execute_query(sql_keys=("WObservation", "Get"),
                                                parameters=(date_part, time_part),
                                                read=True)
        wdata = ",".join( map(str, wdata[0]) )

        # 3) Store it in a file that will be read by the Polybar config file.
        with open("current_wdata", 'w') as f:
            f.write(wdata)

    def run(self):
        """
        Main method to run the application.
        """

        # 1) Check the creation of the WeatherDB
        if not self.weatherDB.exists():
            self.weatherDB.create_db()

        # 2) Get my current location and compare with cached data
        lat, long, country, city = self.ipLocation.get_data()
        if self.needs_update([city, country]):

            # 3) Update WeatherDB
            expires_at = self.update_db(f"{long},{lat}")

            # 4) Write the new location to the cache
            self.locationCache.save_cache((long, lat), city, country, expires_at)

            print("The location has changed and/or the data has expired. Updating DB...")
        else:
            print("NO ACTION: The location was not changed, or the weather data didn't expire!")

        # 5) It will retrieve the current weather data.
        self.update_wdata()


if __name__ == "__main__":
    app = WeatherApp()
    app.run()
