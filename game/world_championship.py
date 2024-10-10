from .match import Match
import random

class WorldChampionship:
    def __init__(self, teams):
        self.teams = teams

    def run(self):
        print("Running World Championship")
        
        # Group Stage
        groups = self.create_groups()
        group_winners = self.run_group_stage(groups)

        # Knockout Stage
        champion = self.run_knockout_stage(group_winners)
        
        print(f"The World Champion is: {champion.name}")

    def create_groups(self):
        random.shuffle(self.teams)
        return [self.teams[i:i+4] for i in range(0, len(self.teams), 4)]

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
            
            group_winners.extend(sorted(standings, key=standings.get, reverse=True)[:2])
            print(f"Group {i+1} Winners: {group_winners[-2].name}, {group_winners[-1].name}")
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
        return rounds[-1][0]