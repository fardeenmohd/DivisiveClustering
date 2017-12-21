import pickle
import requests
import json
from dota_match import DotaMatch
import os
import argparse
API = 'https://api.opendota.com/api/'
PUBLIC_MATCHES = 'publicMatches'
HEROES = 'heroes'
MATCHES = 'matches'


def get_list_of_matche_dicts():
    """Returns a python list of dictionaries containing match data"""
    matches_response = requests.get(API + PUBLIC_MATCHES)
    return json.loads(matches_response.text)


def get_heroes_response():
    return requests.get(API + HEROES)


def get_hero_names():
    """Returns a dictionary of hero_id : int -> hero_name : str"""
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
    parser = argparse.ArgumentParser()
    # The argument is of the form -f or --file.
    # If -f or --file is given... for ex: "main.py -f" but no file is given then the "const" argument specifies the file
    # If no -f or --file option is given at all then the "default" argument specifies the file
    parser.add_argument('-f', '--file', nargs='?', type=str, default='../data/matches.pkl',
                        const='../data/matches.pkl', help='Path to input file containing matches to be read')
    parser.add_argument('-n', '--num-matches', nargs='?', type=int, default=5000,
                        const=5000, help='Maximum number of matches to be collected')
    program_args = vars(parser.parse_args())
    data_file_path = program_args['file']
    num_of_matches = program_args['num_matches']
    collector = DataCollector(data_file_path=data_file_path, max_num_of_matches=num_of_matches)
    collector.collect_and_save_matches()
    list_of_matches = collector.read_dota_matches_from_file()
    print('Found ' + str(len(list_of_matches)) + ' matches from file')
    for match in list_of_matches:
        print(match)