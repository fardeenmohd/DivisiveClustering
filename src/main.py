import requests
import json
from dota_match import DotaMatch
from cluster import Cluster
API = 'https://api.opendota.com/api/'
PUBLIC_MATCHES = 'publicMatches'
HEROES = 'heroes'
MATCHES = 'matches'

if __name__ == '__main__':

    matches_response = requests.get(API + PUBLIC_MATCHES)
    heroes_response = requests.get(API + HEROES)

    list_of_match_dicts = json.loads(matches_response.text)
    list_of_hero_dicts = json.loads(heroes_response.text)

    hero_names_dict = dict()
    list_of_dota_matches = list()

    for hero_dict in list_of_hero_dicts:
        hero_names_dict[hero_dict['id']] = hero_dict['localized_name']

    print('Hero id and names: ' + str(hero_names_dict))

    for match_dict in list_of_match_dicts:
        if match_dict['avg_mmr'] is not None:
            match = DotaMatch(match_dict, hero_names_dict)
            list_of_dota_matches.append(match)
            print(str(match))

    initial_cluster = Cluster(matches=list_of_dota_matches, hero_names=hero_names_dict)
    initial_cluster.print_center()