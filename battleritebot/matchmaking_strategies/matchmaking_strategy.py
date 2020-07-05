from battleritebot.match import Match
from __future__ import annotations
from abc import ABC, abstractmethod

"""
The MatchmakingStrategy interface declares operations common to all supported versions
of an algorithm for assigning teams to a match. Strategies can be changed at runtime.

The bot uses this interface to call the algorithm defined by concrete
MatchmakingStrategies to assign teams to a match.

See: Strategy pattern.
"""
class MatchmakingStrategy(ABC):

    @abstractmethod
    def assign_teams(self, match: Match):
        pass