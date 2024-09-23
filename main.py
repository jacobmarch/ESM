import json
import random
from game.player import Player
from game.team import Team
from game.match import Map, Game
from game.season import Season, Offseason

def load_team_names(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def load_player_names(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def create_sample_players(num_players):
    player_names = load_player_names('data/player_names.json')
    players = []
    roles = ["Sniper", "Assault", "Support", "Scout", "Tank"]

    for _ in range(num_players):
        first_name = random.choice(player_names['first_names'])
        last_name = random.choice(player_names['last_names'])
        gamertag = random.choice(player_names['gamertags'])
        primary_role = random.choice(roles)
        secondary_role = random.choice([r for r in roles if r != primary_role])

        ratings = {
            'aim': random.randint(60, 100),
            'movement': random.randint(60, 100),
            'knowledge': random.randint(60, 100),
            'ability_usage': random.randint(60, 100),
            'leadership': random.randint(60, 100),
            'communication': random.randint(60, 100)
        }

        player = Player(first_name, last_name, gamertag, primary_role, secondary_role, **ratings)
        players.append(player)

    return players

def create_teams(team_names, players):
    teams = []
    for name in team_names:
        team_players = random.sample(players, 5)
        team = Team(name, team_players)
        teams.append(team)
        for player in team_players:
            players.remove(player)
    return teams

def create_maps():
    return [
        Map("Dust II", "attack"),
        Map("Inferno", "defense"),
        Map("Mirage", "attack"),
        Map("Nuke", "defense"),
    ]

def main():
    team_names = load_team_names('data/team_names.txt')
    num_players_needed = len(team_names) * 5 + 10  # Extra players for free agents
    players = create_sample_players(num_players_needed)
    teams = create_teams(team_names, players[:len(team_names) * 5])
    free_agents = players[len(team_names) * 5:]
    maps = create_maps()

    print("Welcome to the League Simulator!")
    print("Available teams:")
    for i, team in enumerate(teams):
        print(f"{i + 1}. {team.team_name}")

    user_choice = int(input("Select your team (enter the number): ")) - 1
    user_team = teams[user_choice]

    offseason = Offseason(teams, free_agents, user_team)
    updated_teams, updated_free_agents = offseason.run_offseason()

    season = Season(updated_teams, maps, user_team)
    season.simulate_season()

if __name__ == "__main__":
    main()