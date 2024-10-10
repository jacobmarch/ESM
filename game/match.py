import random

class Match:
    def __init__(self, home_team, away_team):
        self.home_team = home_team
        self.away_team = away_team

    def play(self):
        home_score = 0
        away_score = 0
        rounds_played = 0

        while True:
            # Play a round
            if random.random() < 0.5:
                home_score += 1
            else:
                away_score += 1
            rounds_played += 1

            # Check for regulation win
            if (home_score >= 13 or away_score >= 13) and abs(home_score - away_score) >= 2:
                break

            # Check for overtime
            if home_score == 12 and away_score == 12:
                while abs(home_score - away_score) < 2:
                    if random.random() < 0.5:
                        home_score += 1
                    else:
                        away_score += 1
                    rounds_played += 1
                break

        if home_score > away_score:
            winner = self.home_team
            loser = self.away_team
        else:
            winner = self.away_team
            loser = self.home_team

        return {
            'home_team': self.home_team,
            'away_team': self.away_team,
            'home_score': home_score,
            'away_score': away_score,
            'winner': winner,
            'loser': loser,
            'rounds_played': rounds_played
        }

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"