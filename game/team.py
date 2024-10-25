import numpy as np
from .player import Player
import random

class Team:
    def __init__(self, name, region):
        self.name = name
        self.region = region
        self.players = []
        self.previous_rating = None  # Store previous year's rating
        
        # Initialize team with 5 players
        for _ in range(5):
            self.players.append(Player())

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
        if not self.players:  # Safety check
            return 0.0
        return np.mean([player.skill for player in self.players])

    def store_previous_rating(self):
        """Store the team's current rating for next season's comparison"""
        self.previous_rating = self.get_average_skill()
    
    def get_rating_change(self):
        """Calculate the change in rating from previous season"""
        if self.previous_rating is None:
            return None
        current_rating = self.get_average_skill()
        return round(current_rating - self.previous_rating, 1)

    def __str__(self):
        return f"{self.name} ({self.region}) - Avg Skill: {self.get_average_skill():.2f}"

    def __repr__(self):
        return self.__str__()
