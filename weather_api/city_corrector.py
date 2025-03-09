from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

class CityCorrector:
    """
    Corrects the spelling of a city name using the Nominatim geocoder.
    """

    def __init__(self, user_agent="weather_app"):
        """
        Initializes the CityCorrector.

        Args:
            user_agent (str, optional): A user agent string for the geocoder.
                                         Nominatim requires a user agent to identify your application.
        """
        self.geolocator = Nominatim(user_agent=user_agent)

    def correct_city_name(self, city):
        """
        Corrects the spelling of a city name.  Prioritizes cities over countries.

        Args:
            city (str): The potentially misspelled city name.

        Returns:
            str: The corrected city name, or None if the city cannot be found.
        """
        try:
            # Limit results to populated places to prioritize cities
            location = self.geolocator.geocode(city, exactly_one=True, timeout=5, featuretype="city")

            if location:
                try:
                    city_name = location.raw.get('name')
                    if city_name:
                        return city_name  # Return 'name' directly

                    # Fallback (less reliable) - only use if name is not present.
                    return location.raw['address'].get('city') or location.raw['address'].get('town') or location.raw['address'].get('village') or location.raw['address'].get('hamlet')

                except KeyError as e:
                    print(f"KeyError accessing address components: {e}")
                    print(f"Raw location data: {location.raw}")  # Print raw data for inspection
                    return None


            else:
                return None  # City not found

        except GeocoderTimedOut:
            print("Geocoding service timed out.")
            return None
        except GeocoderServiceError as e:
            print(f"Geocoding service error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during geocoding: {e}")
            return None



#Test
# city_corrector = CityCorrector()
# corrected_city = city_corrector.correct_city_name('Toshkent')
# print(corrected_city)

# corrected_city = city_corrector.correct_city_name('London')
# print(corrected_city)

# corrected_city = city_corrector.correct_city_name('Tashkent')
# print(corrected_city)

# corrected_city = city_corrector.correct_city_name('Tokio')
# print(corrected_city)