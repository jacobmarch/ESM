from game.manager import GameManager

def main():
    print("Welcome to the Esports Manager Game!")
    print("You'll be guiding your leagues through multiple seasons.")
    print("Use the menu options to navigate through different phases of the game.")
    print("\nLet's begin!")
    input("Press Enter to start the game...")

    game_manager = GameManager()
    game_manager.start_game()

if __name__ == "__main__":
    main()
