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
        Corrects the spelling of a city name.

        Args:
            city (str): The potentially misspelled city name.

        Returns:
            str: The corrected city name, or None if the city cannot be found.
        """
        try:
            location = self.geolocator.geocode(city, timeout=5)  # Adjust timeout as needed

            if location:
                return location.address.split(',')[-1].strip()  # Extract city from address string
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
