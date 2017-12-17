import pickle
import requests
import json
from dota_match import DotaMatch
import os
API = 'https://api.opendota.com/api/'
PUBLIC_MATCHES = 'publicMatches'
HEROES = 'heroes'
MATCHES = 'matches'


def get_list_of_matche_dicts():
    matches_response = requests.get(API + PUBLIC_MATCHES)
    return json.loads(matches_response.text)


def get_heroes_response():
    return requests.get(API + HEROES)


def get_hero_names():
    heroes_response = get_heroes_response()
    list_of_hero_dicts = json.loads(heroes_response.text)
    hero_names_dictionary = dict()
    for hero_dict in list_of_hero_dicts:
        hero_names_dictionary[hero_dict['id']] = hero_dict['localized_name']

    print('Hero id and names: ' + str(hero_names_dictionary))
    return hero_names_dictionary


class DataCollector:

    def __init__(self, max_num_of_matches: int = 10000, data_file_path: str = '../data/matches.pkl'):
        print('FILE: data_collector.py DataCollector() __init__ Current Working Directory: ' + os.getcwd())
        self.max_num_of_matches = max_num_of_matches
        self.data_file_path = data_file_path
        self.hero_names_dict = get_hero_names()

    def collect_and_save_matches(self):
        list_of_dota_matches = list()
        num_of_matches_collected = 0

        while num_of_matches_collected < self.max_num_of_matches:
            list_of_match_dicts = get_list_of_matche_dicts()
            for match_dict in list_of_match_dicts:
                if match_dict['avg_mmr'] is not None:
                    match = DotaMatch(match_dict, self.hero_names_dict)
                    list_of_dota_matches.append(match)
                    num_of_matches_collected += 1
                    print('Collected ' + str(num_of_matches_collected) + ' dota matches')
                    if num_of_matches_collected >= self.max_num_of_matches:
                        break
        output_file = open(self.data_file_path, 'wb')
        pickle.dump(list_of_dota_matches, output_file, pickle.HIGHEST_PROTOCOL)

    def read_dota_matches_from_file(self):
        input_file = open(self.data_file_path, 'rb')
        return pickle.load(input_file)

if __name__ == '__main__':
    collector = DataCollector()
    # collector.collect_and_save_matches()
    list_of_matches = collector.read_dota_matches_from_file()
    print('Found ' + str(len(list_of_matches)) + ' matches from file')
    for match in list_of_matches:
        print(match)