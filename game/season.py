import random
from .match import Match
from .tournament import DoubleEliminationTournament

class Season:
    def __init__(self, teams):
        self.teams = teams
        self.matches = []
        self.standings = {team: 0 for team in teams}

    def run_regular_season(self):
        # Create a list of all possible matchups
        matchups = []
        for i, team1 in enumerate(self.teams):
            for team2 in self.teams[i+1:]:  # Only match with teams not yet played
                # Randomly determine home/away
                if random.random() < 0.5:
                    matchups.append((team1, team2))
                else:
                    matchups.append((team2, team1))
        
        # Shuffle the matchups for variety
        random.shuffle(matchups)
        
        # Play all matches
        for home_team, away_team in matchups:
            match = Match(home_team, away_team)
            result = match.play()
            self.update_standings(result)
            self.matches.append(match)

    def update_standings(self, result):
        self.standings[result['winner']] += 3

    def get_standings(self):
        """Return sorted standings with team and points"""
        return sorted(self.standings.items(), key=lambda x: x[1], reverse=True)

    def get_standings_text(self):
        """Return formatted standings text for storage"""
        standings = self.get_standings()
        text = "Regular Season Standings:\n"
        text += "-" * 40 + "\n"
        
        for i, (team, points) in enumerate(standings, 1):
            text += f"{i}. {team.name:<20} Points: {points}\n"
        
        # Add match results
        text += "\nMatch Results:\n"
        text += "-" * 40 + "\n"
        for match in self.matches:
            result = match.play()
            text += f"{result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name}\n"
        
        return text

    def get_top_teams(self, count):
        sorted_teams = sorted(self.standings.items(), key=lambda x: x[1], reverse=True)
        return [team for team, _ in sorted_teams[:count]]

    def print_standings(self):
        print("\nFinal Standings:")
        sorted_standings = sorted(self.standings.items(), key=lambda x: x[1], reverse=True)
        for team, points in sorted_standings:
            print(f"{team.name}: {points} points")
        print()

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
