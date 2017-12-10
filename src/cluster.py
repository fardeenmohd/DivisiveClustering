from dota_match import DotaMatch
from typing import List
from typing import Dict
import operator
from copy import deepcopy


class Cluster:

    def __init__(self, matches: List[DotaMatch] = None, hero_names: Dict[int, str] = None):
        self.matches = matches
        self.hero_names = hero_names
        self.center = self.get_center()

    def get_center(self) -> DotaMatch:

        num_of_matches = len(self.matches)
        avg_match = deepcopy(self.matches[0])
        victorious_hero_count = {}  # From hero_id -> number of heroes
        lost_hero_count = {}  # From hero_id -> number of heroes

        for hero_id, name in self.hero_names.items():
            victorious_hero_count[hero_id] = 0
            lost_hero_count[hero_id] = 0

        for hero in avg_match.heroes_that_won:
            victorious_hero_count[hero] += 1

        for hero in avg_match.heroes_that_lost:
            lost_hero_count[hero] += 1

        for i in range(1, num_of_matches):
            avg_match.avg_mmr += self.matches[i].avg_mmr
            avg_match.avg_rank_tier += self.matches[i].avg_rank_tier
            avg_match.duration += self.matches[i].duration
            for hero in self.matches[i].heroes_that_won:
                victorious_hero_count[hero] += 1
            for hero in self.matches[i].heroes_that_lost:
                lost_hero_count[hero] += 1

        sorted_victorious_hero_counts = sorted(victorious_hero_count.items(), key=operator.itemgetter(1))
        sorted_lost_hero_counts = sorted(lost_hero_count.items(), key=operator.itemgetter(1))
        # print('Victorious hero counts: ' + str(sorted_victorious_hero_counts))
        # print('Lost hero counts: ' + str(sorted_lost_hero_counts))
        most_common_winning_heroes = sorted_victorious_hero_counts[-5:]
        most_common_winning_heroes = [x[0] for x in most_common_winning_heroes]
        most_common_lost_heroes = sorted_lost_hero_counts[-5:]
        most_common_lost_heroes = [x[0] for x in most_common_lost_heroes]

        avg_match.heroes_that_won = most_common_winning_heroes
        avg_match.heroes_that_lost = most_common_lost_heroes
        avg_match.avg_mmr = int(avg_match.avg_mmr / num_of_matches)
        avg_match.avg_rank_tier = int(avg_match.avg_rank_tier / num_of_matches)
        avg_match.duration = int(avg_match.duration / num_of_matches)

        return avg_match

    def print_center(self):
        print('----------Cluster center information----------')
        heroes_that_won_names = [str(self.hero_names[hero_id]) for hero_id in self.center.heroes_that_won]
        heroes_that_lost_names = [str(self.hero_names[hero_id]) for hero_id in self.center.heroes_that_lost]
        print('Top heroes that won games: ' + str(heroes_that_won_names))
        print('Top heroes that lost games: ' + str(heroes_that_lost_names))
        print('Avg MMR: ' + str(self.center.avg_mmr))
        print('Avg rank tier: ' + str(self.center.avg_rank_tier))
        print('Avg duration: ' + str(self.center.duration))