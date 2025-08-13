from abc import ABC, abstractmethod

import json


format_json = lambda response : json.loads(response.content.decode())

class ExternalAPIService(ABC):
    """
    Abstract base class for external API communication services.

    Provides common functionality for HTTP-based API interactions.
    You can also set how to process the response before using it in
    production.
    """

    def __init__(self, api_key, endpoint):
        super().__init__()
        self.api_key = api_key
        self.endpoint = endpoint

    @abstractmethod
    def _process_data(self):
        """
        Indicate how to process the data retrieved from the API.
        """

    @abstractmethod
    def get_data(self, *args):
        """
        Obtain the data by making the API call.
        """
