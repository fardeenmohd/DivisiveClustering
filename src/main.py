import requests
import json
from dota_match import DotaMatch
import clustering
import time
import data_collector
import argparse


def main(dist_constant: int = None, file_path: str = '../data/matches.pkl', hero_weight: float = 0.05):
    if dist_constant is not None:
        print('main(): dist_constant is: ')
    print('main(): Data file path: ' + file_path)
    print('main(): hero weight: ' + str(hero_weight))
    collector = data_collector.DataCollector(data_file_path=file_path)
    list_of_dota_matches = collector.read_dota_matches_from_file()
    print('main(): DataCollector found: ' + str(len(list_of_dota_matches)) + ' matches from file')
    hero_names_dict = data_collector.get_hero_names()

    # for match_dict in list_of_match_dicts:
    #     if match_dict['avg_mmr'] is not None:
    #         try:
    #             match = DotaMatch(match_dict, hero_names_dict)
    #             list_of_dota_matches.append(match)
    #             print(str(match))
    #         except json.decoder.JSONDecodeError:
    #             print('Caught json.decoder.JSONDecodeError Exception, ignoring match...')
    # print('Query returned ' + str(len(list_of_dota_matches)) + ' matches')

    # Create the initial cluster that contains all matches that were read from file
    initial_cluster = clustering.Cluster(matches=list_of_dota_matches, hero_names=hero_names_dict)
    initial_cluster.print_center()
    max_dist = 0
    num_of_matches = len(initial_cluster.matches)
    farthest_cluster_pair = 0, 0
    avg_dist = 0
    num_of_disjoint_pairs = 0
    if dist_constant is None:
        # Get all disjoint pair distances, and find the average distance between points as well as the maximum distance
        for i in range(num_of_matches):
            for j in range(i + 1, num_of_matches):
                dist = clustering.get_distance(initial_cluster.matches[i], initial_cluster.matches[j],
                                               hero_weight=hero_weight)
                avg_dist += dist
                num_of_disjoint_pairs += 1
                if dist > max_dist:
                    max_dist = dist
                    farthest_cluster_pair = i, j
                    # print('Distance is: ' + str(dist))

        avg_dist = (avg_dist / num_of_disjoint_pairs)
        print('Average distance between Dota matches: ' + str(avg_dist) + ' max dist is: ' + str(max_dist))
    else:
        avg_dist = dist_constant
        print('Using dist constant of: ' + str(avg_dist) + ' max dist is: ' + str(max_dist))

    divisive_clustering_clusters = []
    divisive_start_time = time.time()
    # Run divisive clustering with the initial cluster and use the avg_dist as the "user-defined" constant
    # Time the computation time
    clustering.run_divisive_clustering(initial_cluster, hero_names_dict, int(avg_dist), divisive_clustering_clusters,
                                       hero_weight=hero_weight)
    divisive_end_time = time.time()
    suggested_value_of_k = len(divisive_clustering_clusters)

    print('Num of clusters found in divisive clustering: ' + str(
        len(divisive_clustering_clusters)) + ' Time of computation: %s seconds. About to print centers...' % (
              divisive_end_time - divisive_start_time))
    for cluster in divisive_clustering_clusters:
        print('Number of matches in cluster: ' + str(len(cluster.matches)))
        cluster.print_center()

    reclustering_start_time = time.time()
    # Run K-means using the value of k found by divisive clustering, and using the clusters already found in that step
    # Time the computation time
    k_means_clusters = clustering.k_means(hero_names_dict=hero_names_dict, num_of_clusters=suggested_value_of_k,
                                          final_clusters=divisive_clustering_clusters, hero_weight=hero_weight)
    reclustering_end_time = time.time()
    print('K-Means with re-clustering found clusters for k=' + str(
        len(k_means_clusters)) + ' In %s seconds. About to print centers...' % (
              reclustering_end_time - reclustering_start_time))
    for cluster in k_means_clusters:
        print('Number of matches in cluster: ' + str(len(cluster.matches)))
        cluster.print_center()

    random_start_time = time.time()
    # In order to compare computation time between
    k_means_random_clusters = clustering.k_means(hero_names_dict=hero_names_dict, num_of_clusters=suggested_value_of_k,
                                                 matches=list_of_dota_matches, hero_weight=hero_weight)
    random_end_time = time.time()
    print('K-Means with random initialization found clusters for k=' + str(
        len(k_means_random_clusters)) + ' In %s seconds. About to print centers...' % (
              random_end_time - random_start_time))
    for cluster in k_means_random_clusters:
        print('Number of matches in cluster: ' + str(len(cluster.matches)))
        cluster.print_center()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # The argument is of the form -f or --file.
    # If -f or --file is given... for ex: "main.py -f" but no file is given then the "const" argument specifies the file
    # If no -f or --file option is given at all then the "default" argument specifies the file
    parser.add_argument('-f', '--file', nargs='?', type=str, default='../data/matches.pkl',
                        const='../data/matches.pkl', help='Path to input file containing matches to be read')
    parser.add_argument('-hw', '--hero-weight', nargs='?', type=float, default=0.05,
                        const=0.05, help='The weight assigned to heroes when clustering, between 0 and 1')
    parser.add_argument('-p', '--dist-constant', nargs='?', type=int,
                        const=1000,
                        help='User defined value that represents tbe minimum distance between the maximum-distance pair such that the cluster can be split')
    program_args = vars(parser.parse_args())
    print('Program arguments: ' + str(program_args))
    data_file_path = program_args['file']
    hero_weight = program_args['hero_weight']
    dist_const = program_args['dist_constant']
    main(file_path=data_file_path, hero_weight=hero_weight, dist_constant=dist_const)
