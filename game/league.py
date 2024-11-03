from .season import Season
from .team import Team
from .utils import load_team_names, save_results
from .tournament import DoubleEliminationTournament

class League:
    team_names = load_team_names()

    def __init__(self, name, current_year):
        self.name = name
        self.current_year = current_year
        self.teams = [Team(team_name, self.name) for team_name in self.team_names[name]]
        self.season = None
        self.playoff_results = None
        self.off_season_results = None
        self.preseason_preview = None
        self.playoff_tournament = None

    def run_off_season(self):
        self.off_season_results = []
        results_text = f"Off-Season Results - {self.name}\n"
        results_text += "=" * 50 + "\n"
        
        for team in self.teams:
            team_changes = team.manage_roster()
            self.off_season_results.append((team.name, team_changes))
            
            # Format team changes for storage
            results_text += f"\n{team.name}:\n"
            for change in team_changes:
                results_text += f"  - {change}\n"
        
        save_results(self.current_year, self.name, results_text)

    def run_season_end(self):
        """Called at the end of each season"""
        # Store current ratings for next season comparison
        for team in self.teams:
            team.store_previous_rating()

    def generate_preseason_preview(self):
        """Generate a preview of teams for the upcoming season"""
        # Sort teams by current skill
        sorted_teams = sorted(self.teams, key=lambda x: x.get_average_skill(), reverse=True)
        
        preview = f"\nPreseason Preview - {self.name}\n"
        preview += "=" * 50 + "\n"
        
        # Team Rankings
        preview += "Team Rankings:\n"
        preview += "-" * 40 + "\n"
        for i, team in enumerate(sorted_teams, 1):
            current_rating = round(team.get_average_skill(), 1)
            rating_change = team.get_rating_change()
            
            # Format the rating change if available
            change_str = ""
            if rating_change is not None:
                sign = "+" if rating_change > 0 else ""
                change_str = f" ({sign}{rating_change:.1f})"  # Using :+.1f to always show sign and 1 decimal
            
            preview += f"{i}. {team.name:<20} Rating: {current_rating}{change_str}\n"
        
        # Top Players
        preview += "\nTop Players:\n"
        preview += "-" * 40 + "\n"
        
        # Get all players from all teams with their team info
        all_players = [(player, team) for team in self.teams for player in team.players]
        # Sort by skill
        top_players = sorted(all_players, key=lambda x: x[0].skill, reverse=True)[:10]
        
        for i, (player, team) in enumerate(top_players, 1):
            # Use the player's gamer tag instead of name
            preview += f"{i}. {player.gamer_tag:<20} ({team.name}) - Skill: {player.skill:.1f}\n"
        
        save_results(self.current_year, self.name, preview)
        self.preseason_preview = preview
        return preview

    def run_regular_season(self):
        self.season = Season(self.teams)
        self.season.run_regular_season()
        
        # Format and save regular season results
        results_text = f"\nRegular Season Results - {self.name}\n"
        results_text += "=" * 50 + "\n"
        results_text += self.season.get_standings_text()  # New method needed in Season class
        
        save_results(self.current_year, self.name, results_text)

    def run_playoffs(self):
        if self.season:
            top_teams = self.season.get_top_teams(8)
            self.playoff_tournament = DoubleEliminationTournament(top_teams)
            self.playoff_tournament.run(silent=True)
            self.playoff_results = self.playoff_tournament.get_standings()
            
            # Format and save playoff results
            results_text = f"\nPlayoff Results - {self.name}\n"
            results_text += "=" * 50 + "\n"
            results_text += self.playoff_tournament.get_results_text()  # New method needed
            
            save_results(self.current_year, self.name, results_text)
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
            print(self.preseason_preview)  # Simply print the formatted string
        else:
            # Generate preview if it hasn't been generated yet
            preview = self.generate_preseason_preview()
            print(preview)

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

    def update_year(self, year):
        """Update the current year"""
        self.current_year = year
