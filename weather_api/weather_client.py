import requests
from .city_corrector import CityCorrector  # Import CityCorrector

class WeatherClient:
    """
    A client for fetching weather data from the OpenWeatherMap API.
    Includes city name correction.
    """

    def __init__(self, api_key, base_url="http://api.openweathermap.org/data/2.5/weather", user_agent="weather_app"):
        """
        Initializes the WeatherClient.

        Args:
            api_key (str): Your OpenWeatherMap API key.
            base_url (str, optional): The base URL for the OpenWeatherMap API. Defaults to "http://api.openweathermap.org/data/2.5/weather".
            user_agent (str, optional): User-agent for the geocoder.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.city_corrector = CityCorrector(user_agent=user_agent)  # Initialize CityCorrector
        self.user_agent = user_agent

    def get_weather(self, city, units="metric"):
        """
        Fetches weather data for a given city, correcting the city name if needed.

        Args:
            city (str): The city to fetch weather data for.
            units (str, optional): The units to use for temperature (e.g., "metric", "imperial"). Defaults to "metric".

        Returns:
            dict: A dictionary containing weather data, or None if an error occurred.
        """

        url = f"{self.base_url}?q={city}&appid={self.api_key}&units={units}"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            return self._parse_weather_data(data)

        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return None
        except ValueError as e:
            print(f"Invalid JSON response: {e}")
            return None
        except KeyError as e:
            print(f"Missing data in response: {e}")
            return None

    def _parse_weather_data(self, data):
        """
        Parses the raw weather data from the API response into a simplified dictionary.

        Args:
            data (dict): The raw JSON response from the OpenWeatherMap API.

        Returns:
            dict: A dictionary containing extracted weather information.
        """
        try:
            return {
                'city': data['name'],  # Use 'name' for city name from API
                'temp': data['main']['temp'],
                'desc': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'speed': data['wind']['speed'],
            }
        except KeyError as e:
            print(f"KeyError while parsing weather data: {e}")
            return None