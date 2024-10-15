import random
from .team import Team
from .player import Player

class Match:
    def __init__(self, home_team: Team, away_team: Team, best_of=3):
        self.home_team = home_team
        self.away_team = away_team
        self.best_of = best_of

    def play(self):
        home_wins = 0
        away_wins = 0
        games_to_win = (self.best_of // 2) + 1
        games_played = []

        while home_wins < games_to_win and away_wins < games_to_win:
            home_score, away_score, round_details = self.simulate_game()
            games_played.append((home_score, away_score, round_details))

            if home_score > away_score:
                home_wins += 1
            else:
                away_wins += 1

        winner = self.home_team if home_wins > away_wins else self.away_team
        loser = self.away_team if home_wins > away_wins else self.home_team

        return {
            'home_team': self.home_team,
            'away_team': self.away_team,
            'home_score': home_wins,
            'away_score': away_wins,
            'winner': winner,
            'loser': loser,
            'games': games_played
        }

    def simulate_game(self):
        home_score = 0
        away_score = 0
        round_details = []

        while home_score < 13 and away_score < 13:
            round_winner, round_info = self.simulate_round()
            round_details.append(round_info)
            if round_winner == self.home_team:
                home_score += 1
            else:
                away_score += 1

            # Check for overtime
            if home_score == 12 and away_score == 12:
                while abs(home_score - away_score) < 2:
                    round_winner, round_info = self.simulate_round()
                    round_details.append(round_info)
                    if round_winner == self.home_team:
                        home_score += 1
                    else:
                        away_score += 1

        return home_score, away_score, round_details

    def simulate_round(self):
        home_alive = self.home_team.players.copy()
        away_alive = self.away_team.players.copy()
        encounters = []

        while home_alive and away_alive:
            home_player = random.choice(home_alive)
            away_player = random.choice(away_alive)

            winner, loser = self.simulate_encounter(home_player, away_player)
            encounters.append((winner, loser))

            if winner in home_alive:
                away_alive.remove(loser)
            else:
                home_alive.remove(loser)

        round_winner = self.home_team if home_alive else self.away_team
        round_info = {
            'winner': round_winner,
            'encounters': encounters,
            'last_standing': home_alive if round_winner == self.home_team else away_alive
        }
        return round_winner, round_info

    def simulate_encounter(self, player1: Player, player2: Player):
        skill_diff = player1.skill - player2.skill
        win_probability = 0.5 + (skill_diff / 200)  # Adjust the 200 to fine-tune the impact of skill difference
        win_probability = max(0.1, min(0.9, win_probability))  # Clamp between 0.1 and 0.9

        if random.random() < win_probability:
            return player1, player2
        else:
            return player2, player1

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"
