from dotenv import load_dotenv
import json
import os
import requests

load_dotenv()

API_KEY = os.getenv("API_KEY")
STR_REQ = "https://servizos.meteogalicia.gal/apiv4/"

format_json = lambda response : json.loads(response.content.decode())


class WeatherForecastService:
    """
    Handle communication with the MeteoGalicia API to retrieve the 7-day
    weather data for a specified location.

    This class manages the API requests and uses a data pipeline to process
    the JSON file containing about the temperature, wind and precipitation
    forecasts. The data is then returned in a structured format.

    Methods:
        getWeatherForecasts(coords: str) -> dict
            Send an API request for the weather data for a specified
    """

    def getNumericForecastInfo(self, coords:str) -> dict:
        """
        Get the temperature, wind and precipitation forescasts from a
        given coordinates (format: "long,lan") for the next 7 days.

        Args:
            coords: str
                Coordinates which we want to know the temperature.

        Return
            dict
                Temperatures of the following 7 seven days.
        """
        params = {"API_KEY": API_KEY,
                  "variables": "temperature",
                  "coords": coords}

        response = requests.get(STR_REQ + "getNumericForecastInfo",
                                params=params)

        response = self._processWeatherData(format_json(response))
        return response

    def _processWeatherData(self, data: dict):
        """
        Process the JSON file containing the temperature, wind, and
        precipitation forecasts for the next few days.
        """
        pass
