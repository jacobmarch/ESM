from .player import Player
import random

class Team:
    def __init__(self, name, region):
        self.name = name
        self.region = region
        self.players = [Player() for _ in range(5)]  # 5 players per team

    def manage_roster(self):
        for player in self.players:
            player.decrease_contract_length()
            if player.contract_years_left == 0:
                if random.random() < 0.7:  # 70% chance to renew
                    player.renew_contract()
                    print(f"{self.name}: {player} renewed contract for {player.contract_length} years")
                else:
                    self.players.remove(player)
                    new_player = Player()
                    self.players.append(new_player)
                    print(f"{self.name}: {player} left, {new_player} joined for {new_player.contract_length} years")

    def __str__(self):
        return f"{self.name} ({self.region})"

    def __repr__(self):
        return self.__str__()