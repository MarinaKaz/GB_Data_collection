#Зарегистрироваться на https://openweathermap.org/api и написать функцию,
# которая получает погоду в данный момент для города, название которого получается через input.
# https://openweathermap.org/current

import requests
import json

def get_response(base_url, city_name, api_key):
    url = f'{base_url}?q={city_name}&appid={api_key}'
    response = requests.get(url)
    return response.json()

key = '8c57f7252ccfd74f5eb99f653cf18f90'
url = 'https://api.openweathermap.org/data/2.5/weather'
city = input('Enter city name ')

response_1 = get_response(url, city, key)

print(response_1)

with open('weather.json', 'w') as f:
    json_weather = json.dump(response_1, f)