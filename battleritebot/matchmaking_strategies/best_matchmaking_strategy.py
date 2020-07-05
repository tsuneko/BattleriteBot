from battleritebot.match import Match, Player
from itertools import combinations
from typing import List, int

"""
Finds the "best" team that minimises the absolute elo difference between the sum each teams elo
by brute forcing through the 6 choose 3 = 20 possible combinations, and taking the compliment of the
combination to be the other team. 

This is not globally the best match if more than 6 players queued before a queue pop.
"""
class BestMatchmakingStrategy(MatchmakingStrategy):

    def get_mmr(player : Player, match_format : int):
        return player.get_mmr()[match_format - 1]

    def get_absolute_elo_difference(team_combination : List[Player], truncated_players : List[Player], match_format : int):
        total_elo = sum(map(lambda e: get_mmr(e, match_format), truncated_players))
        team_a_elo = sum(map(lambda e: get_mmr(e, match_format), team_combination))
        team_b_elo = total_elo - team_a_elo
        return abs(team_a_elo - team_b_elo)

    def assign_teams(self, match: Match):
        truncated_players = players[0: (match.format * 2) - 1]

        team_a_combinations = combinations(truncated_players, match.match_format)
        best_team_a = min(team_a_combinations, key=lambda e: get_absolute_elo_difference(e, truncated_players))
        best_team_a_ids = map(lambda e: e.getId(), best_team_a)

        best_team_b = filter(lambda e: e.get_id() not in best_team_a_ids))

        for i in range(match.match_format):
            match.teamA.append([best_team_a[i].username, best_team_a[i].mmr[match.match_format - 1][-1], 0])
            match.teamB.append([best_team_b[i].username, best_team_b[i].mmr[match.match_format - 1][-1], 0])