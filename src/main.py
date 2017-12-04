import requests
import json
API = 'https://api.opendota.com/api/'
PRO_MATCHES = 'proMatches'
PUBLIC_MATCHES = 'publicMatches'
HEROES = 'heroes'

response = requests.get(API + PUBLIC_MATCHES)
json_result = json.loads(response.text)

print(json_result)
