import requests
import json
from dota_match import DotaMatch
import cluster
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
    initial_cluster = cluster.Cluster(matches=list_of_dota_matches, hero_names=hero_names_dict)
    initial_cluster.print_center()
    # Get disjoint pair distances
    for i in range(len(initial_cluster.matches)):
        for j in range(i, len(initial_cluster.matches)):
            if i != j:
                print('Distance is: ' + str(cluster.get_distance(initial_cluster.matches[i], initial_cluster.matches[j])))

    k_means_clusters = cluster.k_means(list_of_dota_matches, hero_names_dict)
    print('Found clusters for k=' + str(len(k_means_clusters)) + ' about to print centers...')
    for cluster in k_means_clusters:
        print('Number of matches in cluster: ' + str(len(cluster.matches)))
        cluster.print_center()