from battleritebot.match import Match, Player
from typing import int

"""
Makes a greedy assignment of teams, trying to minimise the elo difference by sorting and 
assigning the best remaining player to each team at each stage of a draft style picks.

E.g. in the case of 3v3's: {1,3,6} {2,4,5} for sorted teams.
"""
class GreedyMatchmakingStrategy(MatchmakingStrategy):
    
    def get_mmr(player : Player, match_format : int):
        return player.get_mmr()[match_format - 1]

    def assign_teams(self, match: Match):
        sorted_players = match.players.copy().sort(reverse=True, key=lambda e: get_mmr(e, match_format))
        for i in range(match.match_format):
            match.teamA.append([sorted_players[i].username, sorted_players[i].mmr[match.match_format - 1][-1], 0])
            match.teamB.append([sorted_players[i+1].username, sorted_players[i+1].mmr[match.match_format - 1][-1], 0])