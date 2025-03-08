import requests
from django.conf import settings
from .models import WeatherData
from django.utils.timezone import now, localtime, timedelta

def get_weather_data(city):
    api_key = settings.OPENWEATHERMAP_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        humidity = data['main']['humidity']
        speed = data['wind']['speed']

        weather_data, created = WeatherData.objects.get_or_create(
            city=city,
            defaults={
                "temp": temp,
                "desc": desc,
                "humidity": humidity,
                "speed": speed,
                "current_time": now()
            }
        )

        if not created:
            dt = now() - localtime(weather_data.current_time)
            if dt > timedelta(minutes=30):
                print(f'SET WEATHER dt={dt}')
                weather_data.temp = temp
                weather_data.desc = desc
                weather_data.humidity = humidity
                weather_data.speed = speed
                weather_data.current_time = now()
                weather_data.save()

        return {
            'city': weather_data.city,
            'temp': weather_data.temp,
            'desc': weather_data.desc,
            'humidity': weather_data.humidity,
            'speed': weather_data.speed,
        }

    except requests.exceptions.RequestException as e:
        print(f"Qátelik júz berdi: {e}")
        return None
    except KeyError:
        print("Nadurıs format")
        return None