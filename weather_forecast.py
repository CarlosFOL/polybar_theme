from datetime import datetime
from dotenv import load_dotenv
import json
import os
import requests

load_dotenv()

API_KEY = os.getenv("API_KEY")
STR_REQ = "https://servizos.meteogalicia.gal/apiv4/"

format_json = lambda response : json.loads(response.content.decode())
format_isodate = lambda date: (
    datetime.fromisoformat(date).strftime("%Y-%m-%d %H:%M:%S").split())


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
                  "variables": "temperature,wind,precipitation_amount",
                  "coords": coords}

        response = requests.get(STR_REQ + "getNumericForecastInfo",
                                params=params)

        response = self._processWeatherData(format_json(response))
        return response

    def _processWeatherData(self, data: dict):
        """
        Process the JSON file containing the temperature, wind, and
        precipitation forecasts for the next few days.

        Args:
            data: dict
                JSON obtained from the API request.
        """
        # The weather data for each day.
        wdata_day: list = data["features"][0]["properties"]["days"]

        db_wdata = [] # Store each record for each day, variable and value.

        # Iterate over the variables (temperature, wind and precipitation amount)
        for d in wdata_day:
            for var in d["variables"]:
                vname = var["name"]
                for v in var["values"]: # The variable values for each day
                    date, time = format_isodate(v["timeInstant"])
                    value = v["value"] if vname != "wind" else v["moduleValue"]
                    db_wdata.append((vname, date, time, value))

        return db_wdata
