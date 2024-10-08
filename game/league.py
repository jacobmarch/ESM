from .season import Season
from .team import Team
from .utils import load_team_names

class League:
    team_names = load_team_names()

    def __init__(self, name):
        self.name = name
        self.teams = [Team(team_name, self.name) for team_name in self.team_names[name]]
        self.season = None

    def run_off_season(self):
        print(f"Running off-season for {self.name}")
        for team in self.teams:
            team.manage_roster()

    def generate_preseason_preview(self):
        # Sort teams by average player skill
        sorted_teams = sorted(self.teams, key=lambda t: sum(p.skill for p in t.players) / len(t.players), reverse=True)
        
        # Display top 5 teams
        print(f"Top 5 teams in {self.name}:")
        for i, team in enumerate(sorted_teams[:5], 1):
            avg_skill = sum(p.skill for p in team.players) / len(team.players)
            print(f"{i}. {team.name} (Avg. Skill: {avg_skill:.2f})")
        
        # Get all players from all teams
        all_players = [player for team in self.teams for player in team.players]
        
        # Sort players by skill
        sorted_players = sorted(all_players, key=lambda p: p.skill, reverse=True)
        
        # Display top 10 players
        print(f"\nTop 10 players in {self.name}:")
        for i, player in enumerate(sorted_players[:10], 1):
            print(f"{i}. {player} (Skill: {player.skill})")

    def run_regular_season(self):
        self.season = Season(self.teams)
        self.season.run_regular_season()

    def run_playoffs(self):
        if self.season:
            print(f"\n{self.name} Playoffs:")
            self.season.run_playoffs(self.name)
        else:
            print(f"Error: Regular season hasn't been played yet for {self.name}.")

    def get_top_teams(self, count):
        if self.season:
            return self.season.get_top_teams(count)
        else:
            print(f"Error: Season hasn't been played yet for {self.name}.")
            return []