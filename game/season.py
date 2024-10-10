import random
from .match import Match

class Season:
    def __init__(self, teams):
        self.teams = teams
        self.matches = []
        self.standings = {team: 0 for team in teams}

    def run_regular_season(self):
        print("Running regular season")
        for home_team in self.teams:
            for away_team in self.teams:
                if home_team != away_team:
                    match = Match(home_team, away_team)
                    result = match.play()
                    self.update_standings(result)
                    self.matches.append(match)
                    print(f"{result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name} ({result['rounds_played']} rounds)")
        self.print_standings()

    def update_standings(self, result):
        self.standings[result['winner']] += 3

    def get_top_teams(self, count):
        sorted_teams = sorted(self.standings.items(), key=lambda x: x[1], reverse=True)
        return [team for team, _ in sorted_teams[:count]]

    def run_playoffs(self):
        print("Running playoffs")
        top_teams = self.get_top_teams(4)
        semifinals = [
            Match(top_teams[0], top_teams[3]),
            Match(top_teams[1], top_teams[2])
        ]
        print("\nSemi-finals:")
        finalists = []
        for match in semifinals:
            result = match.play()
            print(f"{result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name} ({result['rounds_played']} rounds)")
            finalists.append(result['winner'])
        
        print("\nFinal:")
        final = Match(finalists[0], finalists[1])
        result = final.play()
        print(f"{result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name} ({result['rounds_played']} rounds)")
        champion = result['winner']
        runner_up = result['loser']
        print(f"The champion of the playoffs is: {champion.name}")
        print(f"The runner-up is: {runner_up.name}")

    def print_standings(self):
        print("\nFinal Standings:")
        sorted_standings = sorted(self.standings.items(), key=lambda x: x[1], reverse=True)
        for team, points in sorted_standings:
            print(f"{team.name}: {points} points")
        print()