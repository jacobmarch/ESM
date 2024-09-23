import random
import os

class Map:
    def __init__(self, name, bias):
        self.name = name
        self.bias = bias  # 'attack' or 'defense'

    def __str__(self):
        return f"Map: {self.name} (Bias: {self.bias})"

class Game:
    def __init__(self, team1, team2, game_map):
        self.team1 = team1
        self.team2 = team2
        self.map = game_map
        self.rounds = {team1.team_name: 0, team2.team_name: 0}
        self.current_round = 0
        self.last_round_winner = None

    def play_round(self):
        self.current_round += 1
        # More complex logic based on map bias and team ratings with randomness
        team1_score = sum(player.ratings['aim'] for player in self.team1.players) + random.randint(-50, 50)
        team2_score = sum(player.ratings['aim'] for player in self.team2.players) + random.randint(-50, 50)

        if self.map.bias == 'attack':
            team1_score += 10
        else:
            team2_score += 10

        winner = self.team1 if team1_score > team2_score else self.team2
        self.rounds[winner.team_name] += 1
        self.last_round_winner = winner.team_name

    def check_winner(self):
        for team, score in self.rounds.items():
            if score >= 13 and (score - min(self.rounds.values())) >= 2:
                return self.team1 if team == self.team1.team_name else self.team2
        if self.current_round >= 24:
            # Check who has more rounds
            if self.rounds[self.team1.team_name] > self.rounds[self.team2.team_name]:
                return self.team1
            elif self.rounds[self.team2.team_name] > self.rounds[self.team1.team_name]:
                return self.team2
            else:
                return None  # Draw
        return None

    def display_score(self):
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the terminal
        print(f"Current Score: {self.team1.team_name} {self.rounds[self.team1.team_name]} - {self.rounds[self.team2.team_name]} {self.team2.team_name}")
        if self.last_round_winner:
            print(f"Last Round: {self.last_round_winner} won the round")

    def display_final_score(self, winner):
        if winner is None:
            print(f"The game ended in a draw!")
            print(f"Final Score: {self.team1.team_name} {self.rounds[self.team1.team_name]} - {self.rounds[self.team2.team_name]} {self.team2.team_name}")
        else:
            losing_team = self.team2 if winner == self.team1 else self.team1
            print(f"{winner.team_name} won the game!")
            print(f"Final Score: {winner.team_name} {self.rounds[winner.team_name]} - {self.rounds[losing_team.team_name]} {losing_team.team_name}")

    def play_game(self, user_team=None):
        while True:
            self.play_round()
            self.display_score()
            winner = self.check_winner()
            if winner is not None or self.current_round >= 24:
                self.display_final_score(winner)
                break
            if user_team in (self.team1, self.team2):
                input("Press Enter to continue to the next round...")

        return {
            'winner': winner,
            'loser': self.team2 if winner == self.team1 else self.team1,
            'winner_score': self.rounds[winner.team_name] if winner else self.rounds[self.team1.team_name],
            'loser_score': self.rounds[self.team2.team_name] if winner == self.team1 else self.rounds[self.team1.team_name]
        }
