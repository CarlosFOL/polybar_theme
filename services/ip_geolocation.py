import requests

from .api_service import ExternalAPIService, format_json


ENDPOINT = "https://api.ipgeolocation.io/v2/ipgeo"


class IPGeolocationService(ExternalAPIService):
    """
    Service for retrieving geographic location data from IP addresses.

    Handles API communication with ipgeolocation to convert IP
    addresses into geographic coordinates and location information.
    """

    def __init__(self, api_key):
        super().__init__(api_key=api_key, endpoint=ENDPOINT)

    def _process_data(self, data: dict) -> list:
        """
        Process the JSON file containing the coordinates, name, and
        country data based on the IP address.

        Args:
            data: dict
                Response from ipgeolocation API.
        Returns:
            list
                Processed data.
        """
        # Desired variables
        variables = ["latitude", "longitude", "country_name", "city"]
        location_data = [data["location"][k] for k in variables]

        # Cast the coordinates to float numbers.
        for i in range(2):
            location_data[i] = float(location_data[i])

        return location_data

    def get_data(self) -> list:
        """
        Send an API request to IPGeoLocation to obtain location data
        from the detected IP address.

        Returns:
            list
                The data of the current location
        """
        response = requests.get(self.endpoint, params={"apiKey": self.api_key} )
        response = self._process_data(format_json(response))
        return response
