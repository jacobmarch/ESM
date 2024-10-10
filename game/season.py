import random
from .match import Match
from .tournament import DoubleEliminationTournament

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
                    print(f"{result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name}")
        self.print_standings()

    def update_standings(self, result):
        self.standings[result['winner']] += 3

    def get_top_teams(self, count):
        sorted_teams = sorted(self.standings.items(), key=lambda x: x[1], reverse=True)
        return [team for team, _ in sorted_teams[:count]]

    def run_playoffs(self, league_name):
        print(f"\n{league_name} Playoffs:")
        top_teams = self.get_top_teams(8)  # Get top 8 teams for playoffs
        tournament = DoubleEliminationTournament(top_teams)
        tournament.run()
        final_standings = tournament.get_standings()
        
        print(f"\n{league_name} Playoff Results:")
        for i, team in enumerate(final_standings[:4], 1):
            print(f"{i}. {team.name}")

        return final_standings[:4]  # Return top 4 teams for World Championship qualification

    def print_standings(self):
        print("\nFinal Standings:")
        sorted_standings = sorted(self.standings.items(), key=lambda x: x[1], reverse=True)
        for team, points in sorted_standings:
            print(f"{team.name}: {points} points")
        print()