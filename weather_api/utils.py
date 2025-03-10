from django.conf import settings
from .models import WeatherData
from django.utils.timezone import now, localtime, timedelta
from weather_api.weather_client import WeatherClient  # Import the WeatherClient
from django.core.exceptions import ObjectDoesNotExist


def get_weather_data(city, skip_correction=False):
    """
    Retrieves weather data for a given city.  Uses a cache and external API,
    and attempts to correct the city name.

    Args:
        city (str): The city to get weather data for.

    Returns:
        dict: A dictionary containing weather data, or None if an error occurred.
    """
    api_key = settings.OPENWEATHERMAP_API_KEY
    weather_client = WeatherClient(api_key, user_agent="weather_api")  # Important: Set a unique user agent

    try:
        lat, lon = None, None
        if not skip_correction:
            corrected_city, lat, lon = weather_client.city_corrector.correct_city_name(city)
            if corrected_city:
                print(f"Corrected city name from '{city}' to '{corrected_city}'")
                city = corrected_city
            else:
                print(f"Could not correct city name for '{city}'")
                return None  # If city correction fails, return None

        try:
            weather_data = WeatherData.objects.get(city=city)
        except ObjectDoesNotExist:
            weather_data = WeatherData(
                city=city,
                temp=0,  # Initial dummy values. These will be overwritten on the first valid API call
                desc="",
                humidity=0,
                speed=0,
                current_time=now(),
                latitude=lat,  # Save latitude
                longitude=lon   # Save longitude
            )
            weather_data.save()
            created = True
        else:
            created = False

        # Check if the cache needs to be updated
        dt = now() - localtime(weather_data.current_time)
        if created or dt > timedelta(minutes=30):  # Always update when a new record is created
            print(f'UPDATING WEATHER dt={dt} created={created}')

            # Use stored coordinates if available, otherwise, geocode again
            if weather_data.latitude and weather_data.longitude:
                lat, lon = weather_data.latitude, weather_data.longitude
                print(f"Using stored coordinates: lat={lat}, lon={lon}")
            elif not skip_correction:
                # Geocode again if coordinates are not stored
                corrected_city, lat, lon = weather_client.city_corrector.correct_city_name(city)
                if corrected_city:
                    print(f"Geocoding again for '{city}': lat={lat}, lon={lon}")
                    weather_data.latitude = lat
                    weather_data.longitude = lon
                    weather_data.save()
                else:
                    print(f"Could not geocode '{city}'")
                    return None  # If geocoding fails, return None
            
            if lat is not None and lon is not None:
                api_data = weather_client.get_weather_by_coordinates(lat, lon)  # Fetch data from the API

                if api_data:
                    weather_data.temp = api_data['temp']
                    weather_data.desc = api_data['desc']
                    weather_data.humidity = api_data['humidity']
                    weather_data.speed = api_data['speed']
                    weather_data.current_time = now()
                    weather_data.save()
                else:
                    print("Failed to retrieve weather data from API.")
                    return {
                        'city': weather_data.city,
                        'temp': weather_data.temp,
                        'desc': weather_data.desc,
                        'humidity': weather_data.humidity,
                        'speed': weather_data.speed,
                    }   # Return the  old data if the new api data is None
            else:
                print("Latitude and longitude are missing.")
                return None

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