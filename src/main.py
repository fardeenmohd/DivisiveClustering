import requests
import json
from dota_match import DotaMatch
import clustering
import time

API = 'https://api.opendota.com/api/'
PUBLIC_MATCHES = 'publicMatches'
HEROES = 'heroes'
MATCHES = 'matches'


def get_hero_names():
    list_of_hero_dicts = json.loads(heroes_response.text)
    hero_names_dictionary = dict()
    for hero_dict in list_of_hero_dicts:
        hero_names_dictionary[hero_dict['id']] = hero_dict['localized_name']

    print('Hero id and names: ' + str(hero_names_dictionary))
    return hero_names_dictionary


if __name__ == '__main__':

    matches_response = requests.get(API + PUBLIC_MATCHES)
    heroes_response = requests.get(API + HEROES)

    list_of_match_dicts = json.loads(matches_response.text)
    list_of_dota_matches = list()
    hero_names_dict = get_hero_names()

    for match_dict in list_of_match_dicts:
        if match_dict['avg_mmr'] is not None:
            match = DotaMatch(match_dict, hero_names_dict)
            list_of_dota_matches.append(match)
            print(str(match))
    print('Query returned ' + str(len(list_of_dota_matches)) + ' matches')

    initial_cluster = clustering.Cluster(matches=list_of_dota_matches, hero_names=hero_names_dict)
    initial_cluster.print_center()
    max_dist = 0
    num_of_matches = len(initial_cluster.matches)
    farthest_cluster_pair = 0, 0
    avg_dist = 0
    num_of_disjoint_pairs = 0
    # Get disjoint pair distances
    for i in range(num_of_matches):
        for j in range(i + 1, num_of_matches):
            dist = clustering.get_distance(initial_cluster.matches[i], initial_cluster.matches[j])
            avg_dist += dist
            num_of_disjoint_pairs += 1
            if dist > max_dist:
                max_dist = dist
                farthest_cluster_pair = i, j
            print('Distance is: ' + str(dist))

    avg_dist = (avg_dist / num_of_disjoint_pairs)
    print('Average distance between Dota matches: ' + str(avg_dist) + ' max dist is: ' + str(max_dist))
    divisive_clustering_clusters = []
    divisive_start_time = time.time()
    clustering.run_divisive_clustering(initial_cluster, hero_names_dict, int(avg_dist), divisive_clustering_clusters)
    divisive_end_time = time.time()
    suggested_value_of_k = len(divisive_clustering_clusters)

    print('Num of clusters found in divisive clustering: ' + str(
        len(divisive_clustering_clusters)) + ' Time of computation: %s seconds. About to print centers...' % (
          divisive_end_time - divisive_start_time))
    for cluster in divisive_clustering_clusters:
        print('Number of matches in cluster: ' + str(len(cluster.matches)))
        cluster.print_center()

    reclustering_start_time = time.time()
    k_means_clusters = clustering.k_means(hero_names_dict=hero_names_dict, num_of_clusters=suggested_value_of_k,
                                          final_clusters=divisive_clustering_clusters)
    reclustering_end_time = time.time()
    print('K-Means with re-clustering found clusters for k=' + str(
        len(k_means_clusters)) + ' In %s seconds. About to print centers...' % (
          reclustering_end_time - reclustering_start_time))
    for cluster in k_means_clusters:
        print('Number of matches in cluster: ' + str(len(cluster.matches)))
        cluster.print_center()

    random_start_time = time.time()
    k_means_random_clusters = clustering.k_means(hero_names_dict=hero_names_dict, num_of_clusters=suggested_value_of_k,
                                                 matches=list_of_dota_matches)
    random_end_time = time.time()
    print('K-Means with random initialization found clusters for k=' + str(
        len(k_means_random_clusters)) + ' In %s seconds. About to print centers...' % (
          random_end_time - random_start_time))
    for cluster in k_means_random_clusters:
        print('Number of matches in cluster: ' + str(len(cluster.matches)))
        cluster.print_center()
