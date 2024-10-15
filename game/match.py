import random
import math

class Match:
    def __init__(self, home_team, away_team):
        self.home_team = home_team
        self.away_team = away_team

    def play(self):
        home_skill = self.home_team.get_average_skill()
        away_skill = self.away_team.get_average_skill()
        
        skill_difference = home_skill - away_skill
        base_win_probability = 0.5 + (skill_difference / 200)  # Adjust the 200 to fine-tune the impact of skill difference
        base_win_probability = max(0.1, min(0.9, base_win_probability))  # Clamp between 0.1 and 0.9

        home_score = 0
        away_score = 0

        while True:
            round_win_probability = base_win_probability + random.uniform(-0.1, 0.1)  # Add some randomness
            if random.random() < round_win_probability:
                home_score += 1
            else:
                away_score += 1

            # Check for regulation win
            if home_score == 13 and away_score <= 11:
                break
            if away_score == 13 and home_score <= 11:
                break

            # Check for overtime
            if home_score >= 12 and away_score >= 12:
                if abs(home_score - away_score) == 2:
                    break

        # Ensure the score difference is exactly 2 if a team wins with more than 13 points
        if home_score > 13:
            home_score = away_score + 2
        elif away_score > 13:
            away_score = home_score + 2

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
            'loser': loser
        }

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"