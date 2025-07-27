from dotenv import load_dotenv
import json
import os
import requests

load_dotenv()

API_KEY= os.getenv("API_KEY")
STR_REQ = "https://servizos.meteogalicia.gal/apiv4/"

format_response = lambda response : json.loads(response.content.decode())


class WeatherForecastService:
    """
    Service offers temperature, wind and precipitation forecasts for the
    next 7 days by calling the METEOGALICIA API.
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

        return format_response(response)
