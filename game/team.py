import numpy as np
from .player import Player
import random

class Team:
    def __init__(self, name, region):
        self.name = name
        self.region = region
        self.players = [Player() for _ in range(5)]  # 5 players per team

    def manage_roster(self):
        changes = []
        for player in self.players:
            player.decrease_contract_length()
            if player.contract_years_left == 0:
                if random.random() < 0.7:  # 70% chance to renew
                    player.renew_contract()
                    changes.append(f"{player} renewed contract for {player.contract_length} years")
                else:
                    old_player = player
                    self.players.remove(player)
                    new_player = Player()
                    self.players.append(new_player)
                    changes.append(f"{old_player} left, {new_player} joined for {new_player.contract_length} years")
        return changes

    def get_average_skill(self):
        return np.mean([player.skill for player in self.players])

    def __str__(self):
        return f"{self.name} ({self.region}) - Avg Skill: {self.get_average_skill():.2f}"

    def __repr__(self):
        return self.__str__()
