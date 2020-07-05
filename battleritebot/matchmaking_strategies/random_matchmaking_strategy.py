from battleritebot.match import Match, Player
from random import shuffle

"""
Randomly assigns the teams disregarding elo..
"""
class RandomMatchmakingStrategy(MatchmakingStrategy):

    def assign_teams(self, match: Match):
        shuffled_players = shuffle(match.players.copy().sort())
        for i in range(match.match_format):
            match.teamA.append([shuffled_players[i].username, shuffled_players[i].mmr[match.match_format - 1][-1], 0])
            match.teamB.append([shuffled_players[i+1].username, shuffled_players[i+1].mmr[match.match_format - 1][-1], 0])