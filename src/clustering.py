from dota_match import DotaMatch
from typing import List, Dict, Tuple, Union
import operator
from copy import deepcopy
from math import sqrt
import random


class Cluster:
    """Class that represents a cluster, it has dota matches as its members and has a center"""

    def __init__(self, matches: List[DotaMatch] = None, hero_names: Dict[int, str] = None):
        self.matches = matches
        self.hero_names = hero_names
        self.center = None
        self.update_center()

    def update_center(self):
        """
        Checks all of its members and updates the self.center class member
        """
        # If we have no members then we have no center
        if len(self.matches) == 0:
            self.center = None
            return

        num_of_matches = len(self.matches)
        self.center = deepcopy(self.matches[0])
        victorious_hero_count = {}  # From hero_id -> number of heroes
        lost_hero_count = {}  # From hero_id -> number of heroes

        # Initialize lists used to count of heroes that lost or won
        for hero_id, name in self.hero_names.items():
            victorious_hero_count[hero_id] = 0
            lost_hero_count[hero_id] = 0

        # Count how many heroes won or lost in this cluster
        for hero in self.center.heroes_that_won:
            victorious_hero_count[hero] += 1

        for hero in self.center.heroes_that_lost:
            lost_hero_count[hero] += 1

        # Calculate average of MMR, rank tier and duration
        for i in range(1, num_of_matches):
            self.center.avg_mmr += self.matches[i].avg_mmr
            self.center.avg_rank_tier += self.matches[i].avg_rank_tier
            self.center.duration += self.matches[i].duration
            # Count heroes that won
            for hero in self.matches[i].heroes_that_won:
                victorious_hero_count[hero] += 1
            for hero in self.matches[i].heroes_that_lost:
                lost_hero_count[hero] += 1
        # Sort the dictionary by the amount of wins a hero has
        sorted_victorious_hero_counts = sorted(victorious_hero_count.items(), key=operator.itemgetter(1))
        sorted_lost_hero_counts = sorted(lost_hero_count.items(), key=operator.itemgetter(1))
        # print('Victorious hero counts: ' + str(sorted_victorious_hero_counts))
        # print('Lost hero counts: ' + str(sorted_lost_hero_counts))
        # Find top 5 heroes that win or lose
        most_common_winning_heroes = sorted_victorious_hero_counts[-5:]
        most_common_winning_heroes = [x[0] for x in most_common_winning_heroes]
        most_common_lost_heroes = sorted_lost_hero_counts[-5:]
        most_common_lost_heroes = [x[0] for x in most_common_lost_heroes]

        self.center.heroes_that_won = most_common_winning_heroes
        self.center.heroes_that_lost = most_common_lost_heroes
        # Calculate average mmr/rank tier/duration for this cluster
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


def get_distance(d1: DotaMatch, d2: DotaMatch, hero_weight: float = 0.05) -> int:
    """
    Get's the distance between two dota match objects. (Between d1 and d2)

    Parameters
    ----------
    d1 : DotaMatch
        The first dota match in the pair
    d2 : DotaMatch
        The second dota match in the pair
    hero_weight: float
        Value between 0 and 1 that represents weight of a given hero

    Returns
    -------
    int
        An integer value that represents the distance between d1 and d2
    """
    # Find the euclidean distance of the MMR and duration
    euclid_dist = sqrt((d1.avg_mmr - d2.avg_mmr) ** 2 +
                       (d1.duration - d2.duration) ** 2)
    hero_value = hero_weight * euclid_dist

    # For every hero that won or lost a match in both matches, subtract a percentage of the euclidean distance
    for i in range(len(d1.heroes_that_won)):
        if d1.heroes_that_won[i] in d2.heroes_that_won:
            # print('About to subtract hero value of: ' + str(hero_value) + ' from: ' + str(euclid_dist))
            euclid_dist -= hero_value
        if d1.heroes_that_lost[i] in d2.heroes_that_lost:
            # print('About to subtract hero value of: ' + str(hero_value) + ' from: ' + str(euclid_dist))
            euclid_dist -= hero_value
    if euclid_dist < 0:
        euclid_dist = 0
    return int(euclid_dist)


def get_distance_to_cluster(d1: DotaMatch, c1: Cluster, hero_weight: float = 0.05) -> int:
    """
    Get's the distance between a dota match and a cluster's center

    Parameters
    ----------
    d1 : DotaMatch
        A dota match that will have its distance measured to the cluster
    c1 : Cluster
        The center of this cluster will have its distance measured to d1
    hero_weight: float
        Weight assigned to each hero between 0 and 1

    Returns
    -------
    int
        An integer value that represents the distance between d1 and d2
    """
    # Distance between a match and a cluster is the distance between a match and the cluster's center
    # Find the euclidean distance of the MMR and duration
    euclid_dist = sqrt((d1.avg_mmr - c1.center.avg_mmr) ** 2 +
                       (d1.duration - c1.center.duration) ** 2)
    hero_value = hero_weight * euclid_dist

    # For every hero that won or lost a match in both matches, subtract a percentage of the euclidean distance
    for i in range(len(d1.heroes_that_won)):
        if d1.heroes_that_won[i] in c1.center.heroes_that_won:
            # print('About to subtract hero value of: ' + str(hero_value) + ' from: ' + str(euclid_dist))
            euclid_dist -= hero_value
        if d1.heroes_that_lost[i] in c1.center.heroes_that_lost:
            # print('About to subtract hero value of: ' + str(hero_value) + ' from: ' + str(euclid_dist))
            euclid_dist -= hero_value
    if euclid_dist < 0:
        euclid_dist = 0
    return int(euclid_dist)


def k_means(hero_names_dict: Dict[int, str], num_of_clusters: int = 3,
            max_iters: int = 100, matches: List[DotaMatch] = None, final_clusters: List[Cluster] = None,
            hero_weight: float = 0.05) -> List[Cluster]:
    """
    Get's the distance between a dota match and a cluster's center

    Parameters
    ----------
    hero_names_dict : Dict[int, str]
        A dictionary that stores key-value pairs of hero_id -> hero_name
    num_of_clusters : int
        The (fixed) amount of clusters that will group the data
    max_iters: int
        The maximum amount of iterations the main loop of the algorithm is allowed to run
    matches: List[DotaMatch]
        If this is not none then it is assumed we wish to perform k means with random initialization
        This contains the list of matches to be grouped by k means
    final_clusters: List[Cluster]
        If this variable is not none then we already have the initial clusters and their members,
         with this variable holding those clusters
    hero_weight: float
        Value between 0 and 1 assigned to each hero
    Returns
    -------
    List[Cluster]
        The list clusters obtained by the k-means algorithm
    """

    # final_clusters is None so we need to find 3 random cluster "seeds"
    # We randomly assign every other dota match to each cluster that was randomly selected
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
        # Update cluster centers since they might have new members
        for cluster in final_clusters:
            cluster.update_center()
        # Loop through every cluster
        for i in range(len(final_clusters)):
            j = 0
            # Loop through every dota match in a cluster
            while j < len(final_clusters[i].matches):
                match = final_clusters[i].matches[j]
                distances = []
                # Calculate distance to every cluster
                for k in range(len(final_clusters)):
                    distances.append(get_distance_to_cluster(match, final_clusters[k], hero_weight=hero_weight))
                closest_cluster_idx = distances.index(min(distances))
                # Make the dota match join the new closest cluster
                # Clusters cannot have 0 members so if its last match wants to leave it then
                # do not allow it to do so
                if closest_cluster_idx != i and len(final_clusters[i].matches) > 1:
                    final_clusters[i].matches.remove(match)
                    final_clusters[closest_cluster_idx].matches.append(match)
                    j -= 1
                    has_changed = True
                j += 1
        i += 1
    print('Clustering finished in ' + str(i) + ' iterations, max num of iters: ' + str(max_iters))
    return final_clusters


def split_cluster(cluster_to_be_split: Cluster, hero_names_dict: Dict[int, str], max_dist: int = 1000,
                  hero_weight: float = 0.05) -> Union[Tuple[Cluster, Cluster], None]:
    """
    Get's the distance between a dota match and a cluster's center

    Parameters
    ----------
    cluster_to_be_split : Cluster
        The cluster that may or may not be split in 2 separate clusters
    hero_names_dict : Dict[int, str]
        A dictionary that stores key-value pairs of hero_id -> hero_name
    max_dist: int
        The maximum distance between all pairs of matches must be bigger than this constant for the cluster to be split
    hero_weight: float
        The weight assigned to each hero, a value between 0 and 0.2
    Returns
    -------
    Union[Tuple[Cluster, Cluster], None]
        A tuple of clusters that partition the input cluster or None if the split criteria has not been met
    """
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
            dist = get_distance(cluster_to_be_split.matches[i], cluster_to_be_split.matches[j], hero_weight=hero_weight)
            if dist > max_found_dist:
                farthest_match_pair = i, j
                max_found_dist = dist

    if max_found_dist < max_dist:
        print('split_cluster(): max_found_dist of ' + str(max_found_dist) + ' is less than max_dist of: '
              + str(max_dist) + ', returning None')
        # We only split the cluster if the maximum distance between pairs is greater than a constant
        return None
    # We have found the pair that is farthest apart
    # So now every other dota match joins the closest of the two, forming 2 new clusters
    for i in range(num_of_matches):
        match = cluster_to_be_split.matches[i]
        if get_distance(match, cluster_to_be_split.matches[farthest_match_pair[0]], hero_weight=hero_weight) < \
                get_distance(match, cluster_to_be_split.matches[farthest_match_pair[1]], hero_weight=hero_weight):
            # cluster_to_be_split.matches.remove(match)
            new_clusters[0].matches.append(match)
        else:
            # cluster_to_be_split.matches.remove(match)
            new_clusters[1].matches.append(match)

    new_clusters[0].update_center()
    new_clusters[1].update_center()
    return new_clusters


def run_divisive_clustering(cluster: Cluster, hero_names_dict: Dict[int, str], max_dist: int,
                            final_clusters: List[Cluster], hero_weight: float = 0.05):
    """
    Runs the divisive clustering algorithm recursively

    Parameters
    ----------
    cluster : Cluster
        The inital cluster that should contain all data points
    hero_names_dict : Dict[int, str]
        A dictionary that stores key-value pairs of hero_id -> hero_name
    max_dist: int
        The maximum distance between all pairs of matches must be bigger than this constant for the cluster to be split
    final_clusters:
        The return value that contains all the final clusters than cannot be divided further
    hero_weight: flaot
        Weight of hero between 0 and 1
    """
    new_clusters = split_cluster(cluster, hero_names_dict, max_dist, hero_weight=hero_weight)
    if new_clusters is None:
        # split_cluster() returned None so that means
        # We could not split the input cluster so it is one of our final clusters
        final_clusters.append(cluster)
    else:
        run_divisive_clustering(new_clusters[0], hero_names_dict, max_dist, final_clusters)
        run_divisive_clustering(new_clusters[1], hero_names_dict, max_dist, final_clusters)
