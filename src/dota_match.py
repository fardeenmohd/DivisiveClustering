class DotaMatch:

    def __init__(self, match_dict: dict = None, hero_names:dict = None):
        self.radiant_win = bool(match_dict['radiant_win'])
        self.duration = int(match_dict['duration'])
        self.avg_mmr = match_dict['avg_mmr']
        self.avg_rank_tier = match_dict['avg_rank_tier']
        rad_heroes = match_dict['radiant_team'].split(',')
        dire_heroes = match_dict['dire_team'].split(',')
        self.radiant_heroes = [int(hero_id) for hero_id in rad_heroes]
        self.dire_heroes = [int(hero_id) for hero_id in dire_heroes]

        self.radiant_hero_names = [hero_names[hero_id] for hero_id in self.radiant_heroes]
        self.dire_hero_names = [hero_names[hero_id] for hero_id in self.dire_heroes]

    def __str__(self):
        match_as_str = '------------------------------\n'
        match_as_str += 'Match information: \n'
        if self.radiant_win:
            match_as_str += 'Radiant won \n'
        else:
            match_as_str += 'Dire won \n'
        match_as_str += 'Average MMR: ' + str(self.avg_mmr) + '\n'
        match_as_str += 'Average rank tier: ' + str(self.avg_rank_tier) + '\n'
        match_as_str += 'Radiant heroes: ' + str(self.radiant_hero_names) + '\n'
        match_as_str += 'Dire heroes: ' + str(self.dire_hero_names) + '\n'
        return match_as_str
