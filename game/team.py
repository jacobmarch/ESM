from .player import Player
import random

class Team:
    def __init__(self, name, region):
        self.name = name
        self.region = region
        self.players = [Player() for _ in range(5)]  # 5 players per team

    def manage_roster(self):
        # Simplified roster management
        if random.random() < 0.3:  # 30% chance of a roster change
            leaving_player = random.choice(self.players)
            self.players.remove(leaving_player)
            new_player = Player()
            self.players.append(new_player)
            print(f"{self.name}: {leaving_player} left, {new_player} joined")

    def __str__(self):
        return f"{self.name} ({self.region})"