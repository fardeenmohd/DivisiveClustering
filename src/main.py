import requests
import json
from src.dota_match import DotaMatch
API = 'https://api.opendota.com/api/'
PUBLIC_MATCHES = 'publicMatches'
HEROES = 'heroes'
MATCHES = 'matches'

matches_response = requests.get(API + PUBLIC_MATCHES)
heroes_response = requests.get(API + HEROES)

list_of_match_dicts = json.loads(matches_response.text)
list_of_hero_dicts = json.loads(heroes_response.text)

hero_names_dict = dict()
list_of_dota_matches = list()

for hero_dict in list_of_hero_dicts:
    hero_names_dict[hero_dict['id']] = hero_dict['localized_name']

for match_dict in list_of_match_dicts:
    match = DotaMatch(match_dict, hero_names_dict)
    list_of_dota_matches.append(match)
    print(str(match))
