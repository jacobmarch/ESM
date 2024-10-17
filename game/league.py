from .season import Season
from .team import Team
from .utils import load_team_names
from .tournament import DoubleEliminationTournament

class League:
    team_names = load_team_names()

    def __init__(self, name):
        self.name = name
        self.teams = [Team(team_name, self.name) for team_name in self.team_names[name]]
        self.season = None
        self.playoff_results = None
        self.off_season_results = None
        self.preseason_preview = None
        self.playoff_tournament = None

    def run_off_season(self):
        self.off_season_results = []
        for team in self.teams:
            team_changes = team.manage_roster()
            self.off_season_results.append((team.name, team_changes))

    def generate_preseason_preview(self):
        sorted_teams = sorted(self.teams, key=lambda t: t.get_average_skill(), reverse=True)
        top_teams = sorted_teams[:5]
        all_players = [(player, team) for team in self.teams for player in team.players]
        sorted_players = sorted(all_players, key=lambda x: x[0].skill, reverse=True)
        top_players = sorted_players[:10]

        self.preseason_preview = {
            'top_teams': top_teams,
            'top_players': top_players
        }

    def run_regular_season(self):
        self.season = Season(self.teams)
        self.season.run_regular_season()

    def run_playoffs(self):
        if self.season:
            top_teams = self.season.get_top_teams(8)  # Get top 8 teams for playoffs
            self.playoff_tournament = DoubleEliminationTournament(top_teams)
            self.playoff_tournament.run(silent=True)
            self.playoff_results = self.playoff_tournament.get_standings()
        else:
            print(f"Error: Regular season hasn't been played yet for {self.name}.")

    def display_off_season_results(self):
        if self.off_season_results:
            for team_name, changes in self.off_season_results:
                print(f"{team_name}:")
                for change in changes:
                    print(f"  - {change}")
        else:
            print("No off-season results available.")

    def display_preseason_preview(self):
        if self.preseason_preview:
            print("Top 5 teams:")
            for i, team in enumerate(self.preseason_preview['top_teams'], 1):
                print(f"{i}. {team.name} (Avg. Skill: {team.get_average_skill():.2f})")
            
            print("\nTop 10 players:")
            for i, (player, team) in enumerate(self.preseason_preview['top_players'], 1):
                print(f"{i}. {player} - {team.name}")
        else:
            print("No preseason preview available.")

    def display_regular_season_results(self):
        if self.season:
            self.season.print_standings()
        else:
            print("No regular season results available.")

    def display_playoff_results(self):
        if self.playoff_tournament:
            self.playoff_tournament.display_results()
        else:
            print("No playoff results available.")

    def get_playoff_results(self):
        return self.playoff_results

    def get_top_teams(self, count):
        if self.season:
            return self.season.get_top_teams(count)
        else:
            print(f"Error: Season hasn't been played yet for {self.name}.")
            return []
