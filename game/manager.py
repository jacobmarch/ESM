from .season import Season
from .league import League
from .world_championship import WorldChampionship
import os

class GameManager:
    def __init__(self):
        self.current_year = 2023
        self.leagues = [
            League("Americas", self.current_year),
            League("Europe", self.current_year),
            League("China", self.current_year),
            League("Pacific", self.current_year)
        ]
        self.current_phase = "Off-Season"
        self.phases = ["Off-Season", "Preseason", "Regular Season", "Playoffs", "World Championship"]
        self.world_championship = None

    def start_game(self):
        while True:
            print(f"\n--- Year {self.current_year} ---")
            print(f"Current Phase: {self.current_phase}")
            self.main_menu()

    def main_menu(self):
        while True:
            print("\nMain Menu:")
            for i, league in enumerate(self.leagues, 1):
                print(f"{i}. View {league.name}")
            print(f"{len(self.leagues) + 1}. Advance to Next Phase")
            print(f"{len(self.leagues) + 2}. Exit Game")

            choice = input(f"Enter your choice (1-{len(self.leagues) + 2}): ")

            if choice in [str(i) for i in range(1, len(self.leagues) + 1)]:
                self.view_league(self.leagues[int(choice) - 1])
            elif choice == str(len(self.leagues) + 1):
                self.advance_phase()
            elif choice == str(len(self.leagues) + 2):
                print("Thank you for playing!")
                exit()
            else:
                print("Invalid choice. Please try again.")

    def simulate_current_phase(self):
        print(f"Simulating {self.current_phase}...")
        if self.current_phase == "Off-Season":
            for league in self.leagues:
                league.run_off_season()
        elif self.current_phase == "Preseason":
            for league in self.leagues:
                league.preseason_preview = league.generate_preseason_preview()  # Store the generated preview
        elif self.current_phase == "Regular Season":
            for league in self.leagues:
                league.run_regular_season()
        elif self.current_phase == "Playoffs":
            for league in self.leagues:
                league.run_playoffs()
        elif self.current_phase == "World Championship":
            self.run_world_championship()
        print(f"{self.current_phase} simulation complete.")

    def view_league(self, league):
        if self.current_phase == "Off-Season":
            print(f"\n{league.name} Off-Season Results:")
            league.display_off_season_results()
        elif self.current_phase == "Preseason":
            print(f"\n{league.name} Preseason Preview:")
            league.display_preseason_preview()
        elif self.current_phase == "Regular Season":
            print(f"\n{league.name} Regular Season Results:")
            league.display_regular_season_results()
        elif self.current_phase == "Playoffs":
            print(f"\n{league.name} Playoff Results:")
            league.display_playoff_results()
        input("Press Enter to continue...")

    def advance_phase(self):
        current_index = self.phases.index(self.current_phase)
        if current_index < len(self.phases) - 1:
            self.current_phase = self.phases[current_index + 1]
            print(f"\nAdvancing to {self.current_phase}")
            self.simulate_current_phase()
        else:
            self.current_year += 1
            for league in self.leagues:
                league.update_year(self.current_year)
            self.current_phase = self.phases[0]
            print(f"\nAdvancing to Year {self.current_year}")
            self.simulate_current_phase()
        # Removed: input("Press Enter to continue...")

    def run_world_championship(self):
        print(f"Running World Championship for year {self.current_year}")
        qualified_teams = []
        for league in self.leagues:
            playoff_results = league.get_playoff_results()
            if playoff_results:
                qualified_teams.extend(playoff_results[:4])
            else:
                print(f"Error: Playoffs haven't been run for {league.name}.")
                return

        if len(qualified_teams) == 16:
            self.world_championship = WorldChampionship(qualified_teams)
            self.world_championship.run()
            
            # Save World Championship results
            results_text = f"World Championship Results {self.current_year}\n"
            results_text += "=" * 50 + "\n"
            results_text += self.world_championship.get_results_text()
            
            from .utils import save_results
            save_results(self.current_year, "World_Championship", results_text)
            
            # Display yearly summary
            print("\nGenerating yearly summary...")
            summary_path = os.path.join("previous_results", str(self.current_year), "yearly_summary.txt")
            if os.path.exists(summary_path):
                with open(summary_path, 'r', encoding='utf-8') as f:
                    print("\nYEARLY SUMMARY")
                    print("=" * 50)
                    print(f.read())
                    print("=" * 50)
        
        else:
            print(f"Error: Incorrect number of qualified teams ({len(qualified_teams)}). Expected 16.")

    def simulate_initial_off_season(self):
        print(f"Simulating initial {self.current_phase} for year {self.current_year}...")
        for league in self.leagues:
            league.run_off_season()
        print(f"Initial {self.current_phase} simulation complete.")

    def run_season_end(self):
        """Called at the end of each season"""
        for league in self.leagues:
            league.run_season_end()
