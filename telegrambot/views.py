import requests
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .utils import send_message



def get_or_create_user(telegram_id):
    headers = {'Content-Type': 'application/json'}
    payload = {"username": f"User-{telegram_id}", "password": f"Pass-{telegram_id}"}

    # Login 
    login_url = f"{settings.BASE_URL}/api/auth/login/"
    response = requests.post(login_url, headers=headers, json=payload, verify='/path/to/your/cert.pem')
    if response.status_code == 200:
        return response.json() 

    # Register
    register_url = f"{settings.BASE_URL}/api/auth/register/"
    response = requests.post(register_url, headers=headers, json={**payload, "password2": payload["password"]}, verify='/path/to/your/cert.pem')
    if response.status_code == 201:
        return requests.post(login_url, headers=headers, json=payload, verify='/path/to/your/cert.pem').json() 

    return None  


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        update = json.loads(request.body)

        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            text = message.get('text')
            user = get_or_create_user(chat_id)

            if user is None:
                send_message(chat_id, "Dizimnen ótiwde qátelik júz berdi.")
                return HttpResponse("OK")

            access_token = user['access']
            user_data = user['user_data']
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
                        response = requests.patch(rest_api_url, headers=headers, json=data, verify='/path/to/your/cert.pem') 

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
                        city = user_data['city']
                        if city:
                            weather_api_url = f"{settings.BASE_URL}/api/weather/{city}/"
                            weather_response = requests.get(weather_api_url, headers=headers, verify='/path/to/your/cert.pem')
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
                        weather_response = requests.get(weather_api_url, headers=headers, verify='/path/to/your/cert.pem')
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

        return HttpResponse("OK")
    else:
        return HttpResponse("Tek POST sorawları qabıllanadı.")