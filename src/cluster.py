from dota_match import DotaMatch
from typing import List
from typing import Dict
import operator
from copy import deepcopy
from math import sqrt
import random


class Cluster:

    def __init__(self, matches: List[DotaMatch] = None, hero_names: Dict[int, str] = None):
        self.matches = matches
        self.hero_names = hero_names
        self.center = None
        self.update_center()

    def update_center(self):
        if len(self.matches) == 0:
            self.center = None

        num_of_matches = len(self.matches)
        self.center = deepcopy(self.matches[0])
        victorious_hero_count = {}  # From hero_id -> number of heroes
        lost_hero_count = {}  # From hero_id -> number of heroes

        for hero_id, name in self.hero_names.items():
            victorious_hero_count[hero_id] = 0
            lost_hero_count[hero_id] = 0

        for hero in self.center.heroes_that_won:
            victorious_hero_count[hero] += 1

        for hero in self.center.heroes_that_lost:
            lost_hero_count[hero] += 1

        for i in range(1, num_of_matches):
            self.center.avg_mmr += self.matches[i].avg_mmr
            self.center.avg_rank_tier += self.matches[i].avg_rank_tier
            self.center.duration += self.matches[i].duration
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

        self.center.heroes_that_won = most_common_winning_heroes
        self.center.heroes_that_lost = most_common_lost_heroes
        self.center.avg_mmr = int(self.center.avg_mmr / num_of_matches)
        self.center.avg_rank_tier = int(self.center.avg_rank_tier / num_of_matches)
        self.center.duration = int(self.center.duration / num_of_matches)

        return deepcopy(self.center)

    def print_center(self):
        print('----------Cluster center information----------')
        heroes_that_won_names = [str(self.hero_names[hero_id]) for hero_id in self.center.heroes_that_won]
        heroes_that_lost_names = [str(self.hero_names[hero_id]) for hero_id in self.center.heroes_that_lost]
        print('Top heroes that won games: ' + str(heroes_that_won_names))
        print('Top heroes that lost games: ' + str(heroes_that_lost_names))
        print('Avg MMR: ' + str(self.center.avg_mmr))
        print('Avg rank tier: ' + str(self.center.avg_rank_tier))
        print('Avg duration: ' + str(self.center.duration))


def get_distance(d1: DotaMatch, d2: DotaMatch) -> int:
    euclid_dist = sqrt((d1.avg_mmr - d2.avg_mmr) ** 2 + (d1.avg_rank_tier - d2.avg_rank_tier) ** 2 +
                       (d1.duration - d2.duration) ** 2)
    hero_weight = 0.05
    hero_value = hero_weight * euclid_dist

    for i in range(len(d1.heroes_that_won)):
        for j in range(len(d2.heroes_that_won)):
            if d1.heroes_that_won[i] == d2.heroes_that_won[j]:
                # print('About to subtract hero value of: ' + str(hero_value) + ' from: ' + str(euclid_dist))
                euclid_dist -= hero_value
            if d1.heroes_that_lost[i] == d2.heroes_that_lost[j]:
                # print('About to subtract hero value of: ' + str(hero_value) + ' from: ' + str(euclid_dist))
                euclid_dist -= hero_value
    return int(euclid_dist)


def get_distance_to_cluster(d1: DotaMatch, c1: Cluster) -> int:
    euclid_dist = sqrt((d1.avg_mmr - c1.center.avg_mmr) ** 2 + (d1.avg_rank_tier - c1.center.avg_rank_tier) ** 2 +
                       (d1.duration - c1.center.duration) ** 2)
    hero_weight = 0.05
    hero_value = hero_weight * euclid_dist

    for i in range(len(d1.heroes_that_won)):
        for j in range(len(c1.center.heroes_that_won)):
            if d1.heroes_that_won[i] == c1.center.heroes_that_won[j]:
                # print('About to subtract hero value of: ' + str(hero_value) + ' from: ' + str(euclid_dist))
                euclid_dist -= hero_value
            if d1.heroes_that_lost[i] == c1.center.heroes_that_lost[j]:
                # print('About to subtract hero value of: ' + str(hero_value) + ' from: ' + str(euclid_dist))
                euclid_dist -= hero_value
    return int(euclid_dist)


def k_means(matches: List[DotaMatch], hero_names_dict: Dict[int, str], num_of_clusters: int = 3, max_iters: int = 100) -> List[Cluster]:
    num_of_matches = len(matches)
    initial_cluster_indices = random.sample(range(num_of_matches), num_of_clusters)
    final_clusters = []
    # Create initial clusters with seed
    for idx in initial_cluster_indices:
        final_clusters.append(Cluster(matches=[matches[idx]], hero_names=hero_names_dict))
    # Assign all matches randomly to a cluster
    for idx in range(num_of_matches):
        if idx not in initial_cluster_indices:
            rand_idx = random.randint(0, num_of_clusters - 1)
            final_clusters[rand_idx].matches.append(matches[idx])

    i = 0
    has_changed = True

    while i < max_iters and has_changed:
        has_changed = False
        for cluster in final_clusters:
            cluster.update_center()
        for i in range(len(final_clusters)):
            j = 0
            while j < len(final_clusters[i].matches):
                match = final_clusters[i].matches[j]
                distances = []
                for k in range(len(final_clusters)):
                    distances.append(get_distance_to_cluster(match, final_clusters[k]))
                closest_cluster_idx = distances.index(min(distances))
                if closest_cluster_idx != i and len(final_clusters[i].matches) > 1:
                    final_clusters[i].matches.remove(match)
                    final_clusters[closest_cluster_idx].matches.append(match)
                    j -= 1
                    has_changed = True
                j += 1
        i += 1
    print('Clustering finished in ' + str(i + 1) + ' iterations, max num of iters: ' + str(max_iters))
    return final_clusters
