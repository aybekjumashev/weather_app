from django.conf import settings
from .models import WeatherData
from django.utils.timezone import now, localtime, timedelta
from weather_api.weather_client import WeatherClient  
from django.core.exceptions import ObjectDoesNotExist


def get_weather_data(city, skip_correction=False):
    api_key = settings.OPENWEATHERMAP_API_KEY
    weather_client = WeatherClient(api_key, user_agent="weather_api")  

    try:
        lat, lon = None, None
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
        except ObjectDoesNotExist:
            weather_data = WeatherData(
                city=city,
                temp=0, 
                desc="",
                humidity=0,
                speed=0,
                current_time=now(),
                latitude=lat,  
                longitude=lon   
            )
            weather_data.save()
            created = True
        else:
            created = False

        dt = now() - localtime(weather_data.current_time)
        if created or dt > timedelta(minutes=30):  
            print(f'UPDATING WEATHER dt={dt} created={created}')

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