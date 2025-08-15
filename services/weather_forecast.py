from datetime import datetime

import requests

from .api_service import ExternalAPIService, format_json


ENDPOINT = "https://servizos.meteogalicia.gal/apiv4/"

format_isodate = lambda date: (
    datetime.fromisoformat(date).strftime("%Y-%m-%d %H:%M:%S").split())


class WeatherForecastService(ExternalAPIService):
    """
    Handle communication with the MeteoGalicia API to retrieve the 7-day
    weather data for a specified location.

    This class manages the API requests and uses a data pipeline to process
    the JSON file containing about the temperature, wind and precipitation
    forecasts. The data is then returned in a structured format.

    Methods:
        getWeatherForecasts(coords: str) -> dict
            Send an API request for the weather data for a specified
            coordinates.

        processWeatherData(data: dict)
            Extract the weather data.
    """
    def __init__(self, api_key):
        super().__init__(api_key=api_key, endpoint=ENDPOINT)

    def _process_data(self, data: dict) -> tuple[list[tuple[str, str, str, float]], str]:
        """
        Process the JSON file containing the temperature, wind, and
        precipitation forecasts for the next few days.

        Args:
            data: dict
                JSON obtained from the API request.

        Returns:
            tuple[list[tuple[str, str, str, float]], str]
                Weather data together to the expire date.
        """
        # The weather data for each day.
        wdata_day: list = data["features"][0]["properties"]["days"]

        db_wdata = [] # Store each record for each day, variable and value.

        # Iterate over the variables (temperature, wind and precipitation amount)
        for d in wdata_day:
            if d["variables"] is not None:
                for var in d["variables"]:
                    vname = var["name"]
                    for v in var["values"]: # The variable values for each day
                        date, time = format_isodate(v["timeInstant"])
                        value = v["value"] if vname != "wind" else v["moduleValue"]
                        db_wdata.append((vname, date, time, value))

        end_date = wdata_day[0]["timePeriod"]["end"]["timeInstant"] # For caching

        return db_wdata, end_date

    def get_data(self, coords:str) -> dict:
        """
        Get the temperature, wind and precipitation forescasts from a
        given coordinates (format: "long,lat") for the next 7 days.

        Args:
            coords: str
                Coordinates which we want to know the temperature (long, lan).

        Return
            dict
                Weather data together to expire date.
        """
        params = {"API_KEY": self.api_key,
                  "variables": "temperature,wind,precipitation_amount",
                  "coords": coords}

        response = requests.get(self.endpoint + "getNumericForecastInfo",
                                params=params)

        response = self._process_data(format_json(response))
        return {"data": response[0], "expires_at": response[1]}

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api = os.getenv("API_MG")
    w = WeatherForecastService(api)

    w.get_data('-8.41039,43.36376')
