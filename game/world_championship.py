from .match import Match
import random

class WorldChampionship:
    def __init__(self, teams):
        self.teams = teams
        self.regions = ["Americas", "Europe", "China", "Pacific"]

    def run(self):
        print("Running World Championship")
        
        # Group Stage
        groups = self.create_balanced_groups()
        group_winners = self.run_group_stage(groups)

        if not group_winners:
            print("Error: No group winners determined. Ending World Championship.")
            return

        # Knockout Stage
        champion = self.run_knockout_stage(group_winners)
        
        if champion:
            print(f"The World Champion is: {champion.name}")
        else:
            print("Error: No champion determined.")

    def create_balanced_groups(self):
        # Separate teams by region
        teams_by_region = {region: [] for region in self.regions}
        for team in self.teams:
            for region in self.regions:
                if region in team.region:
                    teams_by_region[region].append(team)
                    break

        # Create balanced groups
        groups = [[] for _ in range(4)]
        for region in self.regions:
            regional_teams = teams_by_region[region]
            random.shuffle(regional_teams)
            for i, team in enumerate(regional_teams):
                groups[i].append(team)

        return groups

    def run_group_stage(self, groups):
        group_winners = []
        for i, group in enumerate(groups):
            print(f"\nGroup {i+1} matches:")
            standings = {team: 0 for team in group}
            for home in group:
                for away in group:
                    if home != away:
                        match = Match(home, away)
                        result = match.play()
                        print(f"{result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name}")
                        standings[result['winner']] += 3
            
            print(f"\nGroup {i+1} Standings:")
            for team, points in sorted(standings.items(), key=lambda x: x[1], reverse=True):
                print(f"{team.name}: {points} points")
            
            top_two = sorted(standings, key=standings.get, reverse=True)[:2]
            group_winners.extend(top_two)
            print(f"Group {i+1} Winners: {top_two[0].name}, {top_two[1].name}")
        return group_winners

    def run_knockout_stage(self, teams):
        print("\nKnockout Stage:")
        rounds = [teams]
        round_names = ["Quarter-finals", "Semi-finals", "Final"]
        for round_name in round_names:
            print(f"\n{round_name}:")
            next_round = []
            for i in range(0, len(rounds[-1]), 2):
                if i+1 < len(rounds[-1]):
                    team1, team2 = rounds[-1][i], rounds[-1][i+1]
                    match = Match(team1, team2)
                    result = match.play()
                    print(f"{result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name}")
                    next_round.append(result['winner'])
                    print(f"Winner: {result['winner'].name}")
            rounds.append(next_round)
        
        return rounds[-1][0] if rounds[-1] else None