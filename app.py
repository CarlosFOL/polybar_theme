import os

from dotenv import load_dotenv

from services import WeatherForecastService, IPGeolocationService
from db.wdb_DAO import WeatherDB

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


    def get_location(self):
        """
        Use the Single IP Geolocation Lookup API from IP Geolocation to
        obtain data about your current location. This data will only be
        stored in the Location table if the country name and/or city are new.
        """


    def update_db(self):
        """
        Make an API request to MeteoGal to obtain the new weather data
        for the next days and update the state of the WeatherData DB.
        """
