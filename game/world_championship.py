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

        # Knockout Stage - Set seeded=True for World Championship format
        knockout_teams = self.create_knockout_matchups(self.group_winners)
        tournament = DoubleEliminationTournament(knockout_teams, seeded=False)
        tournament.run(silent=True)
        self.final_standings = tournament.get_standings()
        
        # Combine group stage and knockout stage results
        self.match_results.extend(tournament.match_results)
        
        self.display_results(self.final_standings)

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
        # Keep first place teams in order (they earned their seeds)
        first_place = group_winners[::2]
        second_place = group_winners[1::2]

        # Create standard bracket matchups:
        # 1st A vs 2nd B
        # 1st C vs 2nd D
        # 1st B vs 2nd A
        # 1st D vs 2nd C
        matchups = []
        pairs = [
            (0, 1), # 1st from A vs 2nd from B
            (2, 3), # 1st from C vs 2nd from D
            (1, 0), # 1st from B vs 2nd from A
            (3, 2)  # 1st from D vs 2nd from C
        ]
        
        for first_idx, second_idx in pairs:
            matchups.append(first_place[first_idx])
            matchups.append(second_place[second_idx])

        return matchups

    def display_results(self, final_standings):
        # Knockout Stage
        print("\n" + "="*50)
        print("KNOCKOUT STAGE")
        print("="*50)
        
        knockout_matches = [match for match in self.match_results if not match[0].startswith("Group")]
        
        rounds = self.organize_matches_into_rounds(knockout_matches)
        
        for round_num, matches in enumerate(rounds, 1):
            print(f"\nRound {round_num}:")
            print("-"*25)
            for round_name, result in matches:
                print(f"{round_name}:")
                self.print_match_result(result)
            print("-"*25)
        
        print("\n" + "="*50)
        print("FINAL STANDINGS")
        print("="*50)
        for i, team in enumerate(final_standings[:4], 1):
            print(f"{i}. {team.name}")

        champion = final_standings[0]
        print("\n" + "*"*50)
        print(f"The World Champion is: {champion.name}".center(50))
        print("*"*50)

    def organize_matches_into_rounds(self, matches):
        rounds = []
        round_sizes = [4, 4, 2, 2, 1, 1]
        current_round = []
        round_index = 0

        for match in matches:
            current_round.append(match)
            if len(current_round) == round_sizes[round_index]:
                rounds.append(current_round)
                current_round = []
                round_index += 1
                if round_index >= len(round_sizes):
                    break

        # Add any remaining matches as a final round
        if current_round:
            rounds.append(current_round)

        return rounds

    def print_match_result(self, result):
        home_team = result['home_team']
        away_team = result['away_team']
        print(f"({home_team.rating:.1f}) {home_team.name} {result['home_score']} - {result['away_score']} {away_team.name} ({away_team.rating:.1f})")
        
        # Calculate map differentials
        temp_match = Match(home_team, away_team)
        map_differentials = {
            map_name: temp_match._calculate_map_scores(home_team, away_team)[map_name] - 
                     temp_match._calculate_map_scores(away_team, home_team)[map_name]
            for map_name in temp_match.available_maps
        }
        
        # Add map sequence with differentials
        print("Map Sequence:")
        for action, team, map_name in result['map_sequence']:
            if action == 'decider':
                print(f"     Decider: {map_name} (Diff: {map_differentials[map_name]:+d})")
            else:
                # Show differential from the picking team's perspective
                diff = map_differentials[map_name] if team == home_team else -map_differentials[map_name]
                print(f"     {team.name} {action}: {map_name} (Diff: {diff:+d})")
        
        # Add map scores
        for game in result['games']:
            home_score, away_score = game['score']
            print(f"     {game['map']}: {home_score}-{away_score}")
        print()

    def get_results_text(self):
        """Return formatted tournament results text for storage"""
        text = "=" * 50 + "\n"
        text += "WORLD CHAMPIONSHIP".center(50) + "\n"
        text += "=" * 50 + "\n\n"
        
        # Group stage results
        text += "GROUP STAGE\n"
        text += "-" * 50 + "\n"
        
        current_group = 1
        for match_type, result in self.match_results:
            if match_type.startswith("Group"):
                if "Group " + str(current_group) in match_type and "Upper Bracket" in match_type:
                    text += f"\nGroup {current_group}:\n"
                    text += "-" * 25 + "\n"
                    current_group += 1
                
                text += f"{match_type}:\n"
                home_team = result['home_team']
                away_team = result['away_team']
                text += f"({home_team.rating:.1f}) {home_team.name} {result['home_score']} - {result['away_score']} {away_team.name} ({away_team.rating:.1f})\n"
                
                # Calculate map differentials
                temp_match = Match(home_team, away_team)
                map_differentials = {
                    map_name: temp_match._calculate_map_scores(home_team, away_team)[map_name] - 
                             temp_match._calculate_map_scores(away_team, home_team)[map_name]
                    for map_name in temp_match.available_maps
                }
                
                # Add map sequence with differentials
                text += "Map Sequence:\n"
                for action, team, map_name in result['map_sequence']:
                    if action == 'decider':
                        text += f"     Decider: {map_name} (Diff: {map_differentials[map_name]:+d})\n"
                    else:
                        # Show differential from the picking team's perspective
                        diff = map_differentials[map_name] if team == home_team else -map_differentials[map_name]
                        text += f"     {team.name} {action}: {map_name} (Diff: {diff:+d})\n"
                
                # Add map scores
                for game in result['games']:
                    home_score, away_score = game['score']
                    text += f"     {game['map']}: {home_score}-{away_score}\n"
                text += "\n"
                
                # Add group winners after the last match of each group
                if "Decider Match" in match_type:
                    winners_match = next(m for m in self.match_results if m[0] == f"Group {current_group-1} Winners' Match")
                    first_seed = winners_match[1]['winner']
                    second_seed = result['winner']
                    
                    text += f"Group {current_group-1} Winners:\n"
                    text += f"1. {first_seed.name}\n"
                    text += f"2. {second_seed.name}\n"
                    text += "-" * 25 + "\n"
        
        # Knockout stage results
        text += "\n" + "=" * 50 + "\n"
        text += "KNOCKOUT STAGE\n"
        text += "=" * 50 + "\n"
        
        knockout_matches = [match for match in self.match_results if not match[0].startswith("Group")]
        rounds = self.organize_matches_into_rounds(knockout_matches)
        
        for round_num, matches in enumerate(rounds, 1):
            text += f"\nRound {round_num}:\n"
            text += "-" * 25 + "\n"
            for round_name, result in matches:
                text += f"{round_name}:\n"
                home_team = result['home_team']
                away_team = result['away_team']
                text += f"({home_team.rating:.1f}) {home_team.name} {result['home_score']} - {result['away_score']} {away_team.name} ({away_team.rating:.1f})\n"
                
                # Calculate map differentials
                temp_match = Match(home_team, away_team)
                map_differentials = {
                    map_name: temp_match._calculate_map_scores(home_team, away_team)[map_name] - 
                             temp_match._calculate_map_scores(away_team, home_team)[map_name]
                    for map_name in temp_match.available_maps
                }
                
                # Add map sequence with differentials
                text += "Map Sequence:\n"
                for action, team, map_name in result['map_sequence']:
                    if action == 'decider':
                        text += f"     Decider: {map_name} (Diff: {map_differentials[map_name]:+d})\n"
                    else:
                        # Show differential from the picking team's perspective
                        diff = map_differentials[map_name] if team == home_team else -map_differentials[map_name]
                        text += f"     {team.name} {action}: {map_name} (Diff: {diff:+d})\n"
                
                # Add map scores
                for game in result['games']:
                    home_score, away_score = game['score']
                    text += f"     {game['map']}: {home_score}-{away_score}\n"
                text += "\n"
            text += "-" * 25 + "\n"
        
        # Final standings
        if hasattr(self, 'final_standings'):
            text += "\n" + "=" * 50 + "\n"
            text += "FINAL STANDINGS\n"
            text += "=" * 50 + "\n"
            for i, team in enumerate(self.final_standings[:4], 1):
                text += f"{i}. {team.name}\n"
            
            champion = self.final_standings[0]
            text += "\n" + "*" * 50 + "\n"
            text += f"The World Champion is: {champion.name}".center(50) + "\n"
            text += "*" * 50 + "\n"
        
        return text
