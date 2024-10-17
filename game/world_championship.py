from .match import Match
from .tournament import DoubleEliminationTournament
import random

class WorldChampionship:
    def __init__(self, teams):
        self.teams = teams
        self.regions = ["Americas", "Europe", "China", "Pacific"]
        self.match_results = []
        self.group_winners = []

    def run(self):
        print("\n" + "="*50)
        print("WORLD CHAMPIONSHIP".center(50))
        print("="*50)
        
        # Group Stage
        groups = self.create_balanced_groups()
        self.run_group_stage(groups)

        if not self.group_winners:
            print("Error: No group winners determined. Ending World Championship.")
            return

        # Knockout Stage
        knockout_teams = self.create_knockout_matchups(self.group_winners)
        tournament = DoubleEliminationTournament(knockout_teams)
        tournament.run(silent=True)
        final_standings = tournament.get_standings()
        
        # Combine group stage and knockout stage results
        self.match_results.extend(tournament.match_results)
        
        self.display_results(final_standings)

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
        print("\nGROUP STAGE")
        print("-"*50)
        for i, group in enumerate(groups):
            print(f"\nGroup {i+1}:")
            print("-"*25)
            
            # Initial upper bracket match
            match1 = Match(group[0], group[1])
            result = match1.play()
            self.match_results.append((f"Group {i+1} Upper Bracket", result))
            self.print_match_result(result)
            upper_winner, upper_loser = result['winner'], result['loser']

            # Initial lower bracket match
            match2 = Match(group[2], group[3])
            result = match2.play()
            self.match_results.append((f"Group {i+1} Lower Bracket", result))
            self.print_match_result(result)
            lower_winner, lower_loser = result['winner'], result['loser']

            # Winners' match (for 1st seed)
            match3 = Match(upper_winner, lower_winner)
            result = match3.play()
            self.match_results.append((f"Group {i+1} Winners' Match", result))
            self.print_match_result(result)
            first_seed, winners_loser = result['winner'], result['loser']

            # Elimination match
            match4 = Match(upper_loser, lower_loser)
            result = match4.play()
            self.match_results.append((f"Group {i+1} Elimination Match", result))
            self.print_match_result(result)
            elim_winner, elim_loser = result['winner'], result['loser']

            # Decider match (for 2nd seed)
            match5 = Match(winners_loser, elim_winner)
            result = match5.play()
            self.match_results.append((f"Group {i+1} Decider Match", result))
            self.print_match_result(result)
            second_seed = result['winner']

            self.group_winners.extend([first_seed, second_seed])
            print(f"\nGroup {i+1} Winners:")
            print(f"1. {first_seed.name}")
            print(f"2. {second_seed.name}")
            print("-"*25)

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

    def display_results(self, final_standings):
        # Knockout Stage
        print("\n" + "="*50)
        print("KNOCKOUT STAGE")
        print("="*50)
        knockout_matches = [match for match in self.match_results if not match[0].startswith("Group")]
        for round_name, result in knockout_matches:
            print(f"\n{round_name}:")
            self.print_match_result(result)
        
        print("\n" + "="*50)
        print("FINAL STANDINGS")
        print("="*50)
        for i, team in enumerate(final_standings[:4], 1):
            print(f"{i}. {team.name}")

        champion = final_standings[0]
        print("\n" + "*"*50)
        print(f"The World Champion is: {champion.name}".center(50))
        print("*"*50)

    def print_match_result(self, result):
        print(f"  {result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name}")
