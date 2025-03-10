import requests

class CityCorrector:
    """
    Corrects the spelling of a city name using the Nominatim geocoder and ensures the result is in English, removing suffixes.
    """

    def __init__(self, user_agent="weather_app"):
        """
        Initializes the CityCorrector.

        Args:
            user_agent (str, optional): A user agent string for the geocoder.
                                         Nominatim requires a user agent to identify your application.
        """
        self.user_agent = user_agent

    def correct_city_name(self, city):
        """
        Corrects the spelling of a city name and returns the result in English, removing suffixes.

        Args:
            city (str): The potentially misspelled city name.

        Returns:
            str: The corrected city name in English, or None if the city cannot be found.
        """
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
                print(f"Raw location data: {location.raw}")  # Print raw data for inspection
                return None, None, None

        except Exception as e:
            print(f"An unexpected error occurred during geocoding: {e}")
            return None








# Test
# city_corrector = CityCorrector()
# corrected_city, lat, lon = city_corrector.correct_city_name('Kungirat')
# print(corrected_city, lat, lon)

# corrected_city, lat, lon = city_corrector.correct_city_name('London')
# print(corrected_city, lat, lon)

# corrected_city, lat, lon = city_corrector.correct_city_name('Tashkent')
# print(corrected_city, lat, lon)

# corrected_city, lat, lon = city_corrector.correct_city_name('Tokio')
# print(corrected_city, lat, lon)

# corrected_city, lat, lon = city_corrector.correct_city_name('New York')
# print(corrected_city, lat, lon)

# corrected_city, lat, lon = city_corrector.correct_city_name('Москва')  # Test a city that's often in another language
# print(corrected_city, lat, lon)

# corrected_city, lat, lon = city_corrector.correct_city_name('Samarkand City')
# print(corrected_city, lat, lon)