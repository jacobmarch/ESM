class Team:
    def __init__(self, team_name, players=None):
        self.team_name = team_name
        self.players = players if players else []

    def add_player(self, player):
        if len(self.players) < 10:
            self.players.append(player)
        else:
            raise ValueError("Cannot add more than 10 players to the team.")

    def remove_player(self, player):
        self.players.remove(player)

    def __str__(self):
        return f"Team {self.team_name} with {len(self.players)} players."
