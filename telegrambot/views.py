import requests
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .utils import send_message  # Ensure this utility exists
import logging # Import logging module

logger = logging.getLogger(__name__) # Initialize logger

def get_or_create_user(telegram_id):
    headers = {'Content-Type': 'application/json'}
    payload = {"username": f"User-{telegram_id}", "password": f"Pass-{telegram_id}"}

    login_url = f"{settings.BASE_URL}/api/auth/login/"
    register_url = f"{settings.BASE_URL}/api/auth/register/"

    try:
        # Login
        logger.debug(f"Attempting login with URL: {login_url}, payload: {payload}")
        response = requests.post(login_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses

        if response.status_code == 200:
            logger.info(f"Login successful for user: User-{telegram_id}")
            return response.json()  # Return login data

        else:
            logger.warning(f"Login failed (status {response.status_code}) for user: User-{telegram_id}, response: {response.text}")
            # Fallback to registration if login fails
            pass  # Fall through to registration attempt

        # Register
        logger.debug(f"Attempting registration with URL: {register_url}, payload: {payload}")
        response = requests.post(register_url, headers=headers, json={**payload, "password2": payload["password"]})
        response.raise_for_status()  # Raise HTTPError

        if response.status_code == 201:
            logger.info(f"Registration successful for user: User-{telegram_id}")

            # Option 1: Rely on the registration endpoint to return login data.
            # return response.json() # Registration endpoint should return token.

            # Option 2: Login immediately after registration
            logger.debug(f"Logging in after registration for user: User-{telegram_id}")
            response = requests.post(login_url, headers=headers, json=payload)
            response.raise_for_status()

            if response.status_code == 200:
                logger.info(f"Login successful after registration for user: User-{telegram_id}")
                return response.json()  # Return login data after registration
            else:
                logger.error(f"Login failed AFTER registration (status {response.status_code}) for user: User-{telegram_id}, response: {response.text}")
                return None

        else:
            logger.error(f"Registration failed (status {response.status_code}) for user: User-{telegram_id}, response: {response.text}")
            return None  # Registration failed

    except requests.exceptions.RequestException as e:  # Catch network errors
        logger.exception(f"Request exception: {e}")
        return None
    except Exception as e: # Catch general exception
        logger.exception(f"An unexpected error occurred: {e}")
        return None


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        update = json.loads(request.body)

        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            text = message.get('text')

            try:  # Wrap the whole function in a try-except block
                user = get_or_create_user(chat_id)

                if user is None:
                    send_message(chat_id, "Dizimnen ótiwde qátelik júz berdi.")
                    return HttpResponse("OK")

                access_token = user.get('access') # Get access token using .get() method
                user_data = user.get('user_data') # Get user data using .get() method

                if not access_token or not user_data: # Verify that access_token and user_data exist
                    logger.error(f"Missing access_token or user_data for chat_id: {chat_id}.  User object: {user}")
                    send_message(chat_id, "Serverde qátelik júz berdi. Iltimas, keyinirek urınıp kóriń.")
                    return HttpResponse("OK")

                headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

                if text:
                    if text == '/start':
                        answer = "Assalawma aleykum!\n/setcity {qala} buyrıǵı arqalı qalańızdı belgileń.\n/weather buyrıǵı arqalı hawa rayı maǵlıwmatların kóriń."
                        send_message(chat_id, answer)

                    elif text.startswith('/setcity'):
                        try:
                            city = text.split()[1]
                            data = {'city': city}
                            rest_api_url = f"{settings.BASE_URL}/api/users/city/"
                            response = requests.patch(rest_api_url, headers=headers, json=data)

                            if response.status_code == 200:
                                answer = f"{city} qalası belgilendi!"
                            else:
                                answer = f"Qátelik júz berdi: {response.status_code}"

                            send_message(chat_id, answer)
                        except IndexError:
                            answer = "Nadurıs format. /setcity {qala} kórinisinde jazıń."
                            send_message(chat_id, answer)
                        except requests.exceptions.RequestException as e:
                            answer = f"API ge soraw jiberiwde qátelik: {e}"
                            send_message(chat_id, answer)

                    elif text == '/weather':
                        try:
                            city = user_data.get('city')  # Access using .get() to avoid KeyError
                            if city:
                                weather_api_url = f"{settings.BASE_URL}/api/weather/{city}/"
                                weather_response = requests.get(weather_api_url, headers=headers)
                                if weather_response.status_code == 200:
                                    weather_data = weather_response.json()
                                    answer = f"{city} qalası hawa rayı:\n\nTemperatura: {weather_data['temp']}\nHalı: {weather_data['desc']}\nÍǵallıq: {weather_data['humidity']}\nSamal tezligi: {weather_data['speed']}"
                                else:
                                    answer = f"Hawa rayı maǵlıwmatların alıwda qátelik: {weather_response.status_code}"
                            else:
                                answer = "Qala belgilenbegen. Iltimas, /setcity {qala} buyrıǵı arqalı qalańızdı belgileń."
                            send_message(chat_id, answer)
                        except requests.exceptions.RequestException as e:
                            answer = f"API ge soraw jiberiwde qátelik: {e}"
                            send_message(chat_id, answer)


                    elif text.startswith('/weather'):
                        try:
                            city = text.split()[1]
                            weather_api_url = f"{settings.BASE_URL}/api/weather/{city}/"
                            weather_response = requests.get(weather_api_url, headers=headers)
                            if weather_response.status_code == 200:
                                weather_data = weather_response.json()
                                answer = f"{city}  qalası hawa rayı:\n\nTemperatura: {weather_data['temp']}\nHalı: {weather_data['desc']}\nÍǵallıq: {weather_data['humidity']}\nSamal tezligi: {weather_data['speed']}"
                            else:
                                answer = f"Hawa rayı maǵlıwmatların alıwda qátelik: {weather_response.status_code}"
                            send_message(chat_id, answer)
                        except IndexError:
                            answer = "Nadurıs format. /weather {qala} kórinisinde jazıń."
                            send_message(chat_id, answer)
                        except requests.exceptions.RequestException as e:
                            answer = f"APIga so'rov yuborishda xatolik: {e}"
                            send_message(chat_id, answer)
                    else:
                        answer = "Túsiniksiz buyrıq."
                        send_message(chat_id, answer)

            except Exception as e: # General error handling in the webhook
                logger.exception(f"An error occurred in telegram_webhook for chat_id: {chat_id}. Update: {update}")
                send_message(chat_id, "Serverde qátelik júz berdi. Iltimas, keyinirek urınıp kóriń.") # General failure message
                return HttpResponse("OK")

        return HttpResponse("OK")
    else:
        return HttpResponse("Tek POST sorawları qabıllanadı.")