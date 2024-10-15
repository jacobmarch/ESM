# Esports Manager Game

## Project Overview
This is an Esports Manager Game simulation where you guide multiple leagues through seasons, playoffs, and a World Championship.

## File Structure and Descriptions

### main.py
The entry point of the application.
- Initializes the game and starts the main loop.

### game/manager.py
Manages the overall game flow.
- `GameManager` class: Handles the yearly cycle of off-season, preseason, regular season, playoffs, and World Championship.

### game/league.py
Represents a regional league.
- `League` class: Manages teams, runs seasons, and conducts playoffs for each region.

### game/season.py
Handles the regular season and playoffs for a league.
- `Season` class: Runs matches, updates standings, and determines top teams.

### game/world_championship.py
Manages the World Championship tournament.
- `WorldChampionship` class: Creates balanced groups, runs group stages, and conducts knockout rounds.

### game/tournament.py
Implements a double elimination tournament system.
- `DoubleEliminationTournament` class: Runs upper and lower bracket matches.

### game/match.py
Simulates individual matches between teams.
- `Match` class: Determines match outcomes based on team skills.

### game/team.py
Represents an esports team.
- `Team` class: Manages players and calculates team skill.

### game/player.py
Represents individual players.
- `Player` class: Handles player attributes, skills, and contracts.

### game/utils.py
Contains utility functions for the game.
- Functions for loading data, generating random names, and other helper methods.

### game/data/
Contains text files with data for the game.
- `first_names.txt`: List of first names for player generation.
- `last_names.txt`: List of last names for player generation.
- `gamer_tags.txt`: List of gamer tags for player generation.
- `team_names.txt`: List of team names organized by region.

## Key Components and Functions

### GameManager (game/manager.py)
- `start_game()`: Main game loop that progresses through each year.
- `run_off_season()`, `run_preseason()`, `run_regular_season()`, `run_playoffs()`, `run_world_championship()`: Methods to handle different phases of the game.

### League (game/league.py)
- `run_off_season()`: Manages team rosters during the off-season.
- `generate_preseason_preview()`: Creates a preview of top teams and players.
- `run_regular_season()`: Conducts the regular season matches.
- `run_playoffs()`: Runs the playoffs for the league.

### Season (game/season.py)
- `run_regular_season()`: Simulates all matches in the regular season.
- `update_standings()`: Updates team standings after each match.
- `get_top_teams()`: Returns the top teams based on standings.

### WorldChampionship (game/world_championship.py)
- `create_balanced_groups()`: Forms balanced groups for the tournament.
- `run_group_stage()`: Conducts the group stage matches.
- `create_knockout_matchups()`: Creates matchups for the knockout stage.
- `run_knockout_stage()`: Runs the knockout stage of the tournament.

### Match (game/match.py)
- `play()`: Simulates a match between two teams and returns the result.

### Team (game/team.py)
- `manage_roster()`: Handles player contracts and roster changes.
- `get_average_skill()`: Calculates the average skill of the team's players.

### Player (game/player.py)
- `improve()`: Increases the player's skill.
- `decrease_contract_length()`: Reduces the remaining contract length.
- `renew_contract()`: Renews the player's contract.

## Data Files
- `first_names.txt`: Contains 2942 first names.
- `last_names.txt`: Contains 158 last names.
- `gamer_tags.txt`: Contains 210 gamer tags.
- `team_names.txt`: Contains team names for 4 regions (Americas, Europe, China, Pacific).

This README provides a comprehensive overview of the project structure, file purposes, and key components. It should help both AI assistants and humans quickly understand the project layout and access the relevant parts of the code for modifications or enhancements.

