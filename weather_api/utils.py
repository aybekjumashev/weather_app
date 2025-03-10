from django.conf import settings
from .models import WeatherData
from django.utils.timezone import now, localtime, timedelta
from weather_api.weather_client import WeatherClient
from django.core.exceptions import ObjectDoesNotExist


def get_weather_data(city, lat=None, lon=None, skip_correction=False):
    """
    Ob-havo ma'lumotlarini oladi, shaharni tuzatadi, saqlangan ma'lumotlarni qaytaradi yoki API dan yangilaydi.

    Args:
        city (str): Shahar nomi.
        lat (float, optional): Kenglik.  Geocodingni chetlab o'tish uchun beriladi. Defaults to None.
        lon (float, optional): Uzunlik.  Geocodingni chetlab o'tish uchun beriladi. Defaults to None.
        skip_correction (bool, optional): Shahar nomini tuzatishni chetlab o'tish. Defaults to False.

    Returns:
        dict: Ob-havo ma'lumotlari lug'ati yoki hech qanday ma'lumot topilmasa None.
    """

    weather_client = WeatherClient(settings.OPENWEATHERMAP_API_KEY, user_agent="weather_api")

    try:
        if not skip_correction:
            corrected_city, lat, lon = weather_client.city_corrector.correct_city_name(city)
            if corrected_city:
                print(f"Corrected city name from '{city}' to '{corrected_city}'")
                city = corrected_city
            else:
                print(f"Could not correct city name for '{city}'")
                return None

        try:
            weather_data = WeatherData.objects.get(city=city)
            created = False
        except ObjectDoesNotExist:
            weather_data = WeatherData(city=city, temp=0, desc="", humidity=0, speed=0, current_time=now(), latitude=lat, longitude=lon)
            weather_data.save()
            created = True

        time_difference = now() - localtime(weather_data.current_time)
        if created or time_difference > timedelta(minutes=30):
            print(f'UPDATING WEATHER dt={time_difference} created={created}')

            # Saqlangan koordinatalardan foydalanish yoki geocode qiling
            if weather_data.latitude and weather_data.longitude:
                lat, lon = weather_data.latitude, weather_data.longitude
                print(f"Using stored coordinates: lat={lat}, lon={lon}")
            elif not skip_correction:
                corrected_city, lat, lon = weather_client.city_corrector.correct_city_name(city)
                if corrected_city:
                    print(f"Geocoding again for '{city}': lat={lat}, lon={lon}")
                    weather_data.latitude = lat
                    weather_data.longitude = lon
                    weather_data.save()
                else:
                    print(f"Could not geocode '{city}'")
                    return None

            if lat is not None and lon is not None:
                api_data = weather_client.get_weather_by_coordinates(lat, lon)

                if api_data:
                    weather_data.temp = api_data['temp']
                    weather_data.desc = api_data['desc']
                    weather_data.humidity = api_data['humidity']
                    weather_data.speed = api_data['speed']
                    weather_data.current_time = now()
                    weather_data.save()
                else:
                    print("Failed to retrieve weather data from API.")
                    # Eski ma'lumotlarni qaytarish
                    return {
                        'city': weather_data.city,
                        'temp': weather_data.temp,
                        'desc': weather_data.desc,
                        'humidity': weather_data.humidity,
                        'speed': weather_data.speed,
                    }
            else:
                print("Latitude and longitude are missing.")
                return None

        # Ma'lumotlarni qaytarish
        return {
            'city': weather_data.city,
            'temp': weather_data.temp,
            'desc': weather_data.desc,
            'humidity': weather_data.humidity,
            'speed': weather_data.speed,
        }

    except Exception as e:
        print(f"Error in get_weather_data: {e}")
        return None