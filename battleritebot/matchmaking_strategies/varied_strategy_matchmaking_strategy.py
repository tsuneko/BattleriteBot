from battleritebot.match import Match, Player
import random

"""
Using composition, this strategy contains other strategies 
and randomly picks one to use for assigning teams.
"""
class VariedStrategyMatchmakingStrategy(MatchmakingStrategy):

    def __init__(self):
        self.strategy_array = [BestMatchmakingStrategy(), GreedyMatchmakingStrategy()]

    def assign_teams(self, match: Match):
        random_index = random.randint(0, len(self.strategyArray)
        selected_strategy = self.strategy_array[randomIndex]
        selected_strategy.assign_teams(self, match)