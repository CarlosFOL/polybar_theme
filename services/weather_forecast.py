from datetime import datetime
import os

from dotenv import load_dotenv
import pandas as pd
import requests

from services.api_service import ExternalAPIService, format_json


ENDPOINT = "https://servizos.meteogalicia.gal/apiv5/"
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
        wdata_day: list[dict[list]] = data["features"][0]["properties"]["days"]

        db_wdata = {var:[] for var in WVARIABLES.split(",")} # Store each record for each day, variable and value.

        # Iterate over the variables (temperature, wind and precipitation amount)
        for day in wdata_day:
            entry: list[dict] = day.get("variables")
            if entry:
                for var in entry: # var \in [temperature, wind, precipitation_amount]
                    vname = var["name"] # variable name
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

    def get_data(self, coords:str, start_time: str) -> dict:
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

        response = self._process_data(format_json(response))
        return {"data": response[0], "expires_at": response[1]}


if __name__ == "__main__":
    load_dotenv()

    api = os.getenv("API_MG")
    wfs = WeatherForecastService(api)
    start_time = datetime.now().strftime("%Y-%m-%dT%H:00:00")

    response = wfs.get_data('-8.41039,43.36376', start_time=start_time)

    # Process data
    db_wdata, end_date = wfs._process_data(response)
    print(db_wdata)
