from .season import Season
from .team import Team
from .utils import load_team_names

class League:
    team_names = load_team_names()

    def __init__(self, name):
        self.name = name
        self.teams = [Team(team_name) for team_name in self.team_names[name]]
        self.season = None

    def run_off_season(self):
        print(f"Running off-season for {self.name}")
        for team in self.teams:
            team.manage_roster()

    def run_regular_season(self):
        self.season = Season(self.teams)
        self.season.run_regular_season()

    def run_playoffs(self):
        if self.season:
            self.season.run_playoffs()
        else:
            print("Error: Regular season hasn't been played yet.")

    def get_top_teams(self, count):
        if self.season:
            return self.season.get_top_teams(count)
        else:
            print("Error: Season hasn't been played yet.")
            return []