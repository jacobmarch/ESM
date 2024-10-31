from game.manager import GameManager
from game.utils import clear_previous_results

def main():
    print("Welcome to the Esports Manager Game!")
    print("You'll be guiding your leagues through multiple seasons.")
    print("Use the menu options to navigate through different phases of the game.")
    print("\nLet's begin!")
    
    # Clear previous results before starting new simulation
    clear_previous_results()
    
    input("Press Enter to start the game...")

    game_manager = GameManager()
    
    # Simulate the first off-season before starting the main game loop
    game_manager.simulate_initial_off_season()
    input("Press Enter to continue...")

    game_manager.start_game()

if __name__ == "__main__":
    main()
