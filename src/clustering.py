from dota_match import DotaMatch
from typing import List, Dict, Tuple, Union
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
            return

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


def k_means(hero_names_dict: Dict[int, str], num_of_clusters: int = 3,
            max_iters: int = 100, matches: List[DotaMatch] = None, final_clusters: List[Cluster] = None) -> List[Cluster]:

    if final_clusters is None:
        final_clusters = []
        num_of_matches = len(matches)
        initial_cluster_indices = random.sample(range(num_of_matches), num_of_clusters)
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
    print('Clustering finished in ' + str(i) + ' iterations, max num of iters: ' + str(max_iters))
    return final_clusters


def split_cluster(cluster_to_be_split: Cluster, hero_names_dict: Dict[int, str], max_dist: int = 1000) -> Union[Tuple[Cluster, Cluster], None]:
    new_clusters = Cluster(matches=[], hero_names=hero_names_dict), Cluster(matches=[], hero_names=hero_names_dict)
    max_found_dist = 0
    num_of_matches = len(cluster_to_be_split.matches)

    if num_of_matches == 1:
        print('split_cluster(): Cluster has only 1 element, returning None')
        return None

    farthest_match_pair = 0, 0

    # Get disjoint pair distances
    for i in range(num_of_matches):
        for j in range(i + 1, num_of_matches):
            dist = get_distance(cluster_to_be_split.matches[i], cluster_to_be_split.matches[j])
            if dist > max_found_dist:
                farthest_match_pair = i, j
                max_found_dist = dist

    if max_found_dist < max_dist:
        print('split_cluster(): max_found_dist of ' + str(max_found_dist) + ' is less than max_dist of: '
              + str(max_dist) + ', returning None')
        # We only split the cluster if the maximum distance between pairs is greater than a constant
        return None

    for i in range(num_of_matches):
        match = cluster_to_be_split.matches[i]
        if get_distance(match, cluster_to_be_split.matches[farthest_match_pair[0]]) < \
                get_distance(match, cluster_to_be_split.matches[farthest_match_pair[1]]):
            # cluster_to_be_split.matches.remove(match)
            new_clusters[0].matches.append(match)
        else:
            # cluster_to_be_split.matches.remove(match)
            new_clusters[1].matches.append(match)

    new_clusters[0].update_center()
    new_clusters[1].update_center()
    return new_clusters


def run_divisive_clustering(cluster: Cluster, hero_names_dict: Dict[int, str], max_dist: int, final_clusters: List[Cluster]):
    new_clusters = split_cluster(cluster, hero_names_dict, max_dist)
    if new_clusters is None:
        # We could not split the input cluster so it is one of our final clusters
        final_clusters.append(cluster)
    else:
        run_divisive_clustering(new_clusters[0], hero_names_dict, max_dist, final_clusters)
        run_divisive_clustering(new_clusters[1], hero_names_dict, max_dist, final_clusters)