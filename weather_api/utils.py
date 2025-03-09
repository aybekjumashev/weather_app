from django.conf import settings
from .models import WeatherData
from django.utils.timezone import now, localtime, timedelta
from weather_api.weather_client import WeatherClient # Import the WeatherClient

def get_weather_data(city):
    """
    Retrieves weather data for a given city.  Uses a cache and external API.

    Args:
        city (str): The city to get weather data for.

    Returns:
        dict: A dictionary containing weather data, or None if an error occurred.
    """
    api_key = settings.OPENWEATHERMAP_API_KEY
    weather_client = WeatherClient(api_key)  # Create an instance of the client

    try:
        weather_data, created = WeatherData.objects.get_or_create(
            city=city,
            defaults={
                "temp": 0,  # Initial dummy values.  These will be overwritten on the first valid API call
                "desc": "",
                "humidity": 0,
                "speed": 0,
                "current_time": now()
            }
        )

        # Check if the cache needs to be updated
        dt = now() - localtime(weather_data.current_time)
        if created or dt > timedelta(minutes=30):  # Always update when a new record is created
            print(f'UPDATING WEATHER dt={dt} created={created}')
            api_data = weather_client.get_weather(city)  # Fetch data from the API

            if api_data:
                weather_data.temp = api_data['temp']
                weather_data.desc = api_data['desc']
                weather_data.humidity = api_data['humidity']
                weather_data.speed = api_data['speed']
                weather_data.current_time = now()
                weather_data.save()
            else:
                print("Failed to retrieve weather data from API.")
                return None  # Or raise an exception if appropriate

        return {
            'city': weather_data.city,
            'temp': weather_data.temp,
            'desc': weather_data.desc,
            'humidity': weather_data.humidity,
            'speed': weather_data.speed,
        }

    except Exception as e:  # Catch broader exceptions
        print(f"Error in get_weather_data: {e}")
        return None