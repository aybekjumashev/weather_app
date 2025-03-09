from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

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
        self.geolocator = Nominatim(user_agent=user_agent)

    def correct_city_name(self, city):
        """
        Corrects the spelling of a city name and returns the result in English, removing suffixes.

        Args:
            city (str): The potentially misspelled city name.

        Returns:
            str: The corrected city name in English, or None if the city cannot be found.
        """
        try:
            # Limit results to populated places to prioritize cities and specify preferred language
            location = self.geolocator.geocode(city, exactly_one=True, timeout=5, featuretype="city")

            if location:
                try:
                    city_name = location.raw.get('name')
                    if city_name:
                        # Remove suffixes like "shahri", "city", etc.
                        city_name = self._remove_city_suffix(city_name)
                        city_name = self._replace_city_chr(city_name)
                        return city_name  # Return cleaned name

                    # Fallback (less reliable) - only use if name is not present.
                    city_name = location.raw['address'].get('city') or location.raw['address'].get('town') or location.raw['address'].get('village') or location.raw['address'].get('hamlet')
                    if city_name:
                        city_name = self._remove_city_suffix(city_name)
                        city_name = self._replace_city_chr(city_name)
                        return city_name
                    else:
                        return None


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

    def _remove_city_suffix(self, city_name: str):
        """Removes common city suffixes from the city name, case-insensitive."""
        suffixes = ["shahri", "city", "town", "village", "посёлок", "город", "of"]  # Add more suffixes as needed
        city_name = city_name.lower() #convert to lowercase
        for suffix in suffixes:
            if suffix in city_name: #convert to lowercase too, for comparison
                city_name = city_name.replace(suffix, '') 
                city_name = city_name.strip()
        return city_name.title()  # If no suffix is removed, still title case.
    
    def _replace_city_chr(self, city_name):
        chrs = {'ı': 'i','ú': 'u','ń': 'n','ó': 'o','á': 'a','ǵ': 'g'}
        city_name = city_name.lower()
        for old_chr, new_chr in chrs.items():
            if old_chr in city_name:
                city_name = city_name.replace(old_chr, new_chr)
        return city_name.title()





# Test
# city_corrector = CityCorrector()
# corrected_city = city_corrector.correct_city_name('Kungirat')
# print(corrected_city)

# corrected_city = city_corrector.correct_city_name('London')
# print(corrected_city)

# corrected_city = city_corrector.correct_city_name('Tashkent')
# print(corrected_city)

# corrected_city = city_corrector.correct_city_name('Tokio')
# print(corrected_city)

# corrected_city = city_corrector.correct_city_name('New York city')
# print(corrected_city)

# corrected_city = city_corrector.correct_city_name('Москва')  # Test a city that's often in another language
# print(corrected_city)

# corrected_city = city_corrector.correct_city_name('Samarkand City')
# print(corrected_city)