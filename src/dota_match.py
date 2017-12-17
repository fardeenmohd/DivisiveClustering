import requests
import json

API = 'https://api.opendota.com/api/'
MATCHES = 'matches/'


class DotaMatch:

    def __init__(self, match_dict: dict = None, hero_names: dict = None):
        self.match_id = match_dict['match_id']
        self.radiant_win = bool(match_dict['radiant_win'])
        self.dire_win = not self.radiant_win
        self.duration = int(match_dict['duration'])
        self.avg_mmr = match_dict['avg_mmr']
        self.avg_rank_tier = match_dict['avg_rank_tier']

        rad_heroes = match_dict['radiant_team'].split(',')
        dire_heroes = match_dict['dire_team'].split(',')

        self.radiant_heroes = [int(hero_id) for hero_id in rad_heroes]
        self.dire_heroes = [int(hero_id) for hero_id in dire_heroes]

        self.radiant_hero_names = [hero_names[hero_id] for hero_id in self.radiant_heroes]
        self.dire_hero_names = [hero_names[hero_id] for hero_id in self.dire_heroes]

        # match_response = requests.get(API + MATCHES + str(self.match_id))
        # match_info_dict = json.loads(match_response.text)
        #
        # self.dire_score = match_info_dict['dire_score']
        # self.radiant_score = match_info_dict['radiant_score']
        #
        # self.dire_barracks_status = match_info_dict['barracks_status_dire']
        # self.radiant_barracks_status = match_info_dict['barracks_status_radiant']
        #
        # self.dire_towers_status = match_info_dict['tower_status_dire']
        # self.radiant_towers_status = match_info_dict['tower_status_radiant']

        self.heroes_that_won = []
        self.heroes_that_lost = []

        if self.radiant_win:
            self.heroes_that_won = [int(hero_id) for hero_id in rad_heroes]
            self.heroes_that_lost = [int(hero_id) for hero_id in dire_heroes]
        else:
            self.heroes_that_won = [int(hero_id) for hero_id in dire_heroes]
            self.heroes_that_lost = [int(hero_id) for hero_id in rad_heroes]

    def __str__(self):

        match_as_str = '*******************************************\n'
        match_as_str += 'Match information: \n'
        match_as_str += 'Match ID: ' + str(self.match_id) + '\n'
        match_as_str += 'Match duration: ' + str(self.duration) + '\n'

        match_as_str += 'Average MMR: ' + str(self.avg_mmr) + '\n'
        match_as_str += 'Average rank tier: ' + str(self.avg_rank_tier) + '\n'

        match_as_str += '----- Radiant statistics -----' '\n'
        match_as_str += 'Radiant won: ' + str(self.radiant_win) + '\n'
        # match_as_str += 'Radiant score: ' + str(self.radiant_score) + '\n'
        match_as_str += 'Radiant heroes: ' + str(self.radiant_hero_names) + '\n'
        # match_as_str += 'Radiant barrack status: ' + str(self.radiant_barracks_status) + '\n'
        # match_as_str += 'Radiant tower status: ' + str(self.radiant_towers_status) + '\n'

        match_as_str += '----- Dire statistics -----' '\n'
        match_as_str += 'Dire won: ' + str(self.dire_win) + '\n'
        # match_as_str += 'Dire score: ' + str(self.dire_score) + '\n'
        match_as_str += 'Dire heroes: ' + str(self.dire_hero_names) + '\n'
        # match_as_str += 'Dire barrack status: ' + str(self.dire_barracks_status) + '\n'
        # match_as_str += 'Dire tower status: ' + str(self.dire_towers_status) + '\n'

        return match_as_str
