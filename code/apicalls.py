import requests

# Put your  CENT Ischool IoT Portal API KEY here.
APIKEY = "4d77f52dba477a9ef22b16f8"

def get_google_place_details(google_place_id: str) -> dict:
    header = { 'X-API-KEY': APIKEY }
    params = { 'place_id': google_place_id }
    url = "https://cent.ischool-iot.net/api/google/places/details"
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()
    return response.json()  # Return the JSON response as a dictionary


def get_azure_sentiment(text: str) -> dict:
    header = { 'X-API-KEY': APIKEY }
    data = { "text" : text }
    url = "https://cent.ischool-iot.net/api/azure/sentiment"
    response = requests.post(url, headers=header, data=data)
    response.raise_for_status()
    return response.json()  # Return the JSON response as a dictionary

def get_azure_key_phrase_extraction(text: str) -> dict:
    header = { 'X-API-KEY': APIKEY }
    data = { "text" : text }
    url = "https://cent.ischool-iot.net/api/azure/keyphrasextraction"
    response = requests.post(url, headers=header, data=data)
    response.raise_for_status()
    return response.json()  # Return the JSON response as a dictionary

def get_azure_named_entity_recognition(text: str) -> dict:
    header = { 'X-API-KEY': APIKEY }
    data = { "text" : text }
    url = "https://cent.ischool-iot.net/api/azure/entityrecognition"
    response = requests.post(url, headers=header, data=data)
    response.raise_for_status()
    return response.json()  # Return the JSON response as a dictionary


def geocode(place:str) -> dict:
    header = { 'X-API-KEY': APIKEY }
    params = { 'location': place }
    url = "https://cent.ischool-iot.net/api/google/geocode"
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()
    return response.json()  # Return the JSON response as a dictionary


def get_weather(lat: float, lon: float) -> dict:
    header = { 'X-API-KEY': APIKEY }
    params = { 'lat': lat, 'lon': lon, 'units': 'imperial' }
    url = "https://cent.ischool-iot.net/api/weather/current"
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()
    return response.json()  # Return the JSON response as a dictionary