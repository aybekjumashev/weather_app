import requests

class CityCorrector:
    def __init__(self, user_agent="weather_app"):
        self.user_agent = user_agent

    def correct_city_name(self, city):
        try:
            base_url = "https://nominatim.openstreetmap.org/search"
            headers = {
                'User-Agent': self.user_agent
            }
            params = {
                "q": city,
                "format": "json",
                "limit": 1  
            }
            response = requests.get(base_url, headers=headers, params=params)

            try:
                data = response.json()
                location = data[0]
                city_name = location.get('name')
                if city_name:
                    return city_name, location.get('lat'), location.get('lon')

                city_name = location['address'].get('city') or location['address'].get('town') or location['address'].get('village') or location['address'].get('hamlet')
                if city_name:
                    return city_name, location.get('lat'), location.get('lon')
                else:
                    return None, None, None


            except Exception as e:
                print(f"KeyError accessing address components: {e}")
                print(f"Raw location data: {location.raw}")  
                return None, None, None

        except Exception as e:
            print(f"An unexpected error occurred during geocoding: {e}")
            return None, None, None



