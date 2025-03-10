import requests
from .city_corrector import CityCorrector  

class WeatherClient:
    def __init__(self, api_key, base_url="http://api.openweathermap.org/data/2.5/weather", user_agent="weather_app"):
        self.api_key = api_key
        self.base_url = base_url
        self.city_corrector = CityCorrector(user_agent=user_agent)  
        self.user_agent = user_agent

    def get_weather(self, city, units="metric"):
        url = f"{self.base_url}?q={city}&appid={self.api_key}&units={units}"

        try:
            response = requests.get(url)
            response.raise_for_status() 
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

    def get_weather_by_coordinates(self, latitude, longitude, units="metric"):
        url = f"{self.base_url}?lat={latitude}&lon={longitude}&appid={self.api_key}&units={units}"

        try:
            response = requests.get(url)
            response.raise_for_status()  
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
        try:
            return {
                'city': data['name'],  
                'temp': data['main']['temp'],
                'desc': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'speed': data['wind']['speed'],
            }
        except KeyError as e:
            print(f"KeyError while parsing weather data: {e}")
            return None