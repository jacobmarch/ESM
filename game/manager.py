from .season import Season
from .league import League
from .world_championship import WorldChampionship

class GameManager:
    def __init__(self):
        self.leagues = [
            League("Americas"),
            League("Europe"),
            League("China"),
            League("Pacific")
        ]
        self.current_year = 2023

    def start_game(self):
        while True:
            print(f"\n--- Year {self.current_year} ---")
            self.run_off_season()
            input("Press Enter to view the preseason preview...")
            
            self.run_preseason()
            input("Press Enter to start the regular season...")
            
            self.run_regular_season()
            input("Press Enter to start the playoffs...")
            
            self.run_playoffs()
            input("Press Enter to start the World Championship...")
            
            self.run_world_championship()
            
            self.current_year += 1
            input("Press Enter to advance to the next year...")

    def run_off_season(self):
        print(f"\nRunning off-season for year {self.current_year}")
        for league in self.leagues:
            print(f"\n{league.name} Off-Season:")
            league.run_off_season()

    def run_preseason(self):
        print(f"\nPreseason Preview for year {self.current_year}")
        for league in self.leagues:
            print(f"\n{league.name} Preseason Preview:")
            league.generate_preseason_preview()

    def run_regular_season(self):
        print(f"Running regular season for year {self.current_year}")
        for league in self.leagues:
            print(f"\n{league.name} Regular Season:")
            league.run_regular_season()

    def run_playoffs(self):
        print(f"Running playoffs for year {self.current_year}")
        for league in self.leagues:
            league.run_playoffs()

    def run_world_championship(self):
        print(f"Running World Championship for year {self.current_year}")
        qualified_teams = []
        for league in self.leagues:
            qualified_teams.extend(league.get_top_teams(4))
        
        world_championship = WorldChampionship(qualified_teams)
        world_championship.run()