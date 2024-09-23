import random
from itertools import combinations
from game.match import Game

class Offseason:
    def __init__(self, teams, free_agents, user_team):
        self.teams = teams
        self.free_agents = free_agents
        self.user_team = user_team

    def run_offseason(self):
        print("\nWelcome to the Offseason!")
        self.user_team_changes()
        self.ai_team_changes()
        return self.teams, self.free_agents

    def user_team_changes(self):
        for _ in range(2):
            print("\nYour current team:")
            for i, player in enumerate(self.user_team.players):
                print(f"{i + 1}. {player}")
            
            print("\nAvailable free agents:")
            for i, player in enumerate(self.free_agents):
                print(f"{i + 1}. {player}")
            
            choice = input("Enter the number of the player you want to sign (or 'skip' to keep your current roster): ")
            if choice.lower() == 'skip':
                break
            
            player_to_sign = self.free_agents[int(choice) - 1]
            player_to_replace = int(input("Enter the number of the player you want to replace: ")) - 1
            
            self.free_agents.append(self.user_team.players[player_to_replace])
            self.user_team.players[player_to_replace] = player_to_sign
            self.free_agents.remove(player_to_sign)

    def ai_team_changes(self):
        for team in self.teams:
            if team != self.user_team:
                for _ in range(2):
                    if random.random() < 0.7:  # 70% chance to make a change
                        player_to_sign = max(self.free_agents, key=lambda p: p.overall_rating)
                        player_to_replace = min(team.players, key=lambda p: p.overall_rating)
                        
                        if player_to_sign.overall_rating > player_to_replace.overall_rating:
                            self.free_agents.append(player_to_replace)
                            team.players.remove(player_to_replace)
                            team.players.append(player_to_sign)
                            self.free_agents.remove(player_to_sign)

class Season:
    def __init__(self, teams, maps, user_team):
        self.teams = teams
        self.maps = maps
        self.user_team = user_team
        self.schedule = self.generate_schedule()
        self.standings = {team: {"wins": 0, "losses": 0} for team in teams}

    def generate_schedule(self):
        schedule = []
        weeks = (len(self.teams) - 1) * 2  # Each team plays every other team twice
        for week in range(weeks):
            week_matches = []
            teams_copy = self.teams.copy()
            random.shuffle(teams_copy)
            while len(teams_copy) > 1:
                home = teams_copy.pop()
                away = teams_copy.pop()
                week_matches.append((home, away))
            schedule.append(week_matches)
        return schedule

    def simulate_season(self):
        print("\nRegular Season")
        for week, matches in enumerate(self.schedule, 1):
            print(f"\nWeek {week}")
            self.simulate_week(matches)
            self.display_standings()

        self.run_playoffs()

    def simulate_week(self, matches):
        for home, away in matches:
            if home == self.user_team or away == self.user_team:
                self.simulate_user_game(home, away)
            else:
                self.simulate_ai_game(home, away)

    def simulate_user_game(self, home, away):
        print(f"\n{home.team_name} vs {away.team_name}")
        game = Game(home, away, random.choice(self.maps))
        result = game.play_game(user_team=self.user_team)
        self.update_standings(result)
        if result['winner']:
            print(f"Final score: {result['winner'].team_name} {result['winner_score']} - {result['loser_score']} {result['loser'].team_name}")
        else:
            print(f"The game ended in a draw: {home.team_name} {result['winner_score']} - {result['loser_score']} {away.team_name}")

    def simulate_ai_game(self, home, away):
        game = Game(home, away, random.choice(self.maps))
        result = game.play_game()
        self.update_standings(result)
        if result['winner']:
            print(f"{result['winner'].team_name} defeats {result['loser'].team_name} {result['winner_score']}-{result['loser_score']}")
        else:
            print(f"{home.team_name} and {away.team_name} draw {result['winner_score']}-{result['loser_score']}")

    def update_standings(self, result):
        if result['winner']:
            self.standings[result['winner']]["wins"] += 1
            self.standings[result['loser']]["losses"] += 1
        else:
            # In case of a draw, both teams get a tie (counted as half a win)
            self.standings[result['winner']]["wins"] += 0.5
            self.standings[result['loser']]["wins"] += 0.5

    def display_standings(self):
        print("\nCurrent Standings:")
        sorted_standings = sorted(self.standings.items(), key=lambda x: (x[1]["wins"], -x[1]["losses"]), reverse=True)
        for team, record in sorted_standings:
            print(f"{team.team_name}: {record['wins']}W - {record['losses']}L")

    def run_playoffs(self):
        print("\nPlayoffs")
        playoff_teams = sorted(self.standings.items(), key=lambda x: (x[1]["wins"], -x[1]["losses"]), reverse=True)[:4]
        semifinals = [
            (playoff_teams[0][0], playoff_teams[3][0]),
            (playoff_teams[1][0], playoff_teams[2][0])
        ]

        print("Semifinals:")
        winners = []
        for home, away in semifinals:
            print(f"\n{home.team_name} vs {away.team_name}")
            game = Game(home, away, random.choice(self.maps))
            result = game.play_game(user_team=self.user_team if self.user_team in (home, away) else None)
            winners.append(result['winner'])
            print(f"{result['winner'].team_name} advances to the finals!")

        print("\nThird Place Game:")
        third_place_teams = [team for team in (semifinals[0][0], semifinals[0][1], semifinals[1][0], semifinals[1][1]) if team not in winners]
        third_place_game = Game(third_place_teams[0], third_place_teams[1], random.choice(self.maps))
        third_place_result = third_place_game.play_game(user_team=self.user_team if self.user_team in third_place_teams else None)

        print("\nChampionship (Best of 3):")
        championship_winner = self.play_championship(winners[0], winners[1])

        self.display_final_results(championship_winner, winners, third_place_result['winner'])

    def play_championship(self, team1, team2):
        team1_wins = 0
        team2_wins = 0
        maps_played = []

        while team1_wins < 2 and team2_wins < 2:
            available_maps = [map for map in self.maps if map not in maps_played]
            current_map = random.choice(available_maps)
            maps_played.append(current_map)

            print(f"\nMap: {current_map.name}")
            game = Game(team1, team2, current_map)
            result = game.play_game(user_team=self.user_team if self.user_team in (team1, team2) else None)

            if result['winner'] == team1:
                team1_wins += 1
            else:
                team2_wins += 1

            print(f"Current score: {team1.team_name} {team1_wins} - {team2_wins} {team2.team_name}")

        return team1 if team1_wins > team2_wins else team2

    def display_final_results(self, champion, runners_up, third_place):
        print("\nFinal Results:")
        print(f"Champion: {champion.team_name}")
        print(f"Runner-up: {runners_up[0].team_name if runners_up[0] != champion else runners_up[1].team_name}")
        print(f"Third Place: {third_place.team_name}")

        print("\nFinal Standings:")
        sorted_standings = sorted(self.standings.items(), key=lambda x: (x[1]["wins"], -x[1]["losses"]), reverse=True)
        for i, (team, record) in enumerate(sorted_standings, 1):
            print(f"{i}. {team.team_name}: {record['wins']}W - {record['losses']}L")