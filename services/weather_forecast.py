from datetime import datetime
import os

from dotenv import load_dotenv
import json
import pandas as pd
import requests

from .api_service import ExternalAPIService, format_json


ENDPOINT = "https://servizos.meteogalicia.gal/apiv4/"
WVARIABLES = "temperature,wind,precipitation_amount"

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


    def _merge_data(self, data: dict) -> tuple[list[tuple[str, str, float, float, float]]]:
        """
        Create a unique table where each row contains the values of the
        weather variable for each day and time.

        Args:
            data: dict
                The data for temperature, wind, and precipitation for
                each day.

        Returns:
            tuple[list[tuple[str, str, float, float, float]], str]
                Weather data in one table
        """
        get_cols = lambda wvar: ["date", "time", wvar]

        wvar = WVARIABLES.split(",")
        df_weather = pd.DataFrame(data[wvar[0]], columns=get_cols(wvar[0]))

        for var in wvar[1:]:
            wdata = data[var]
            df_weather = pd.merge(left=df_weather,
                                  right=pd.DataFrame( wdata, columns=get_cols(var) ),
                                  on = ["date", "time"]
                                  )

        return df_weather


    def _process_data(self, data: dict) -> tuple[list[tuple[str, str, float, float, float]], str]:
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

        db_wdata = {var:[] for var in WVARIABLES.split(",")} # Store each record for each day, variable and value.

        # Iterate over the variables (temperature, wind and precipitation amount)
        for d in wdata_day:
            if d["variables"] is not None:
                for var in d["variables"]:
                    vname = var["name"]
                    for v in var["values"]: # The variable values for each day
                        date, time = format_isodate(v["timeInstant"])
                        value = v["value"] if vname != "wind" else v["moduleValue"]
                        db_wdata[vname].append((date, time, value))

        # For caching. It could be used any wvariable to obtain the end date.
        end_date = db_wdata["temperature"][-1]
        end_date = f"{end_date[0]}T{end_date[1]}"

        # Combine all the information
        db_wdata = self._merge_data(db_wdata)

        return db_wdata, end_date

    def get_data(self, coords:str, start_time: str, raw: bool = False) -> dict:
        """
        Get the temperature, wind and precipitation forescasts from a
        given coordinates (format: "long,lat") for the next 7 days.

        Args:
            coords: str
                Coordinates which we want to know the temperature (long, lan).
            start_time: str
                From that moment on, the data is recovered.

        Return
            dict
                Weather data together to expire date.
        """
        params = {"API_KEY": self.api_key,
                  "variables": WVARIABLES,
                  "coords": coords,
                  "startTime": start_time}

        response = requests.get(self.endpoint + "getNumericForecastInfo",
                                params=params)

        if not raw:
            response = self._process_data(format_json(response))
            return {"data": response[0], "expires_at": response[1]}
        else:
            return format_json(response)


if __name__ == "__main__":
    load_dotenv()

    api = os.getenv("API_MG")
    wfs = WeatherForecastService(api)
    raw = False

    response = wfs.get_data('-8.41039,43.36376', raw=raw)

    if raw:
        # Store JSON with location data
        with open("../tmp/location_data.json", "w") as f:
            f.write(json.dumps(response, indent=2))
    else:
        print(response["expires_at"])
