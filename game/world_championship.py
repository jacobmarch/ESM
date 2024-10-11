from .match import Match
from .tournament import DoubleEliminationTournament
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
        print("\nWorld Championship Knockout Stage:")
        knockout_teams = self.create_knockout_matchups(group_winners)
        tournament = DoubleEliminationTournament(knockout_teams)
        tournament.run()
        final_standings = tournament.get_standings()
        
        print("\nWorld Championship Final Standings:")
        for i, team in enumerate(final_standings[:4], 1):
            print(f"{i}. {team.name}")

        champion = final_standings[0]
        print(f"\nThe World Champion is: {champion.name}")

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
            
            # Initial upper bracket match
            match1 = Match(group[0], group[1])
            result = match1.play()
            print(f"Upper Bracket: {result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name}")
            upper_winner, upper_loser = result['winner'], result['loser']

            # Initial lower bracket match
            match2 = Match(group[2], group[3])
            result = match2.play()
            print(f"Lower Bracket: {result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name}")
            lower_winner, lower_loser = result['winner'], result['loser']

            # Winners' match (for 1st seed)
            match3 = Match(upper_winner, lower_winner)
            result = match3.play()
            print(f"Winners' Match: {result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name}")
            first_seed, winners_loser = result['winner'], result['loser']

            # Elimination match
            match4 = Match(upper_loser, lower_loser)
            result = match4.play()
            print(f"Elimination Match: {result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name}")
            elim_winner, elim_loser = result['winner'], result['loser']

            # Decider match (for 2nd seed)
            match5 = Match(winners_loser, elim_winner)
            result = match5.play()
            print(f"Decider Match: {result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name}")
            second_seed = result['winner']

            group_winners.extend([first_seed, second_seed])
            print(f"Group {i+1} Winners: 1. {first_seed.name}, 2. {second_seed.name}")

        return group_winners

    def create_knockout_matchups(self, group_winners):
        # Separate 1st and 2nd place teams
        first_place = group_winners[::2]
        second_place = group_winners[1::2]

        # Shuffle second place teams
        random.shuffle(second_place)

        # Create matchups ensuring teams from the same group don't face each other
        matchups = []
        for i, team in enumerate(first_place):
            # Find a second place team not from the same group
            for opponent in second_place:
                if opponent not in group_winners[i*2:(i+1)*2]:
                    matchups.append(team)
                    matchups.append(opponent)
                    second_place.remove(opponent)
                    break

        return matchups

    def run_knockout_stage(self, teams):
        print("\nKnockout Stage:")
        
        # Separate 1st and 2nd seeds
        first_seeds = teams[::2]
        second_seeds = teams[1::2]
        
        # Shuffle second seeds to avoid matching with teams from the same group
        random.shuffle(second_seeds)
        
        # Create quarter-final matchups
        quarter_finals = list(zip(first_seeds, second_seeds))
        
        rounds = [quarter_finals]
        round_names = ["Quarter-finals", "Semi-finals", "Final"]
        
        for round_name in round_names:
            print(f"\n{round_name}:")
            next_round = []
            for match in rounds[-1]:
                team1, team2 = match
                match_obj = Match(team1, team2)
                result = match_obj.play()
                print(f"{result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name}")
                next_round.append(result['winner'])
                print(f"Winner: {result['winner'].name}")
            
            if len(next_round) > 1:
                # Pair teams for the next round
                rounds.append(list(zip(next_round[::2], next_round[1::2])))
            else:
                # Final round
                return next_round[0]
        
        return None