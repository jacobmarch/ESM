from .match import Match

class DoubleEliminationTournament:
    def __init__(self, teams, seeded=True):
        self.teams = teams
        self.upper_bracket = self._create_seeded_bracket(teams) if seeded else teams.copy()
        self.lower_bracket = []
        self.upper_bracket_losers = []
        self.results = []
        self.grand_finalist = None
        self.match_results = []

    def _create_seeded_bracket(self, teams):
        if len(teams) != 8:
            return teams.copy()
            
        # For World Championship, teams are already properly ordered
        # by create_knockout_matchups, so just return them in order
        return teams.copy()

    def run(self, silent=False):
        round_count = 0
        max_rounds = 20  # Safeguard against infinite loops

        while (len(self.upper_bracket) > 1 or len(self.lower_bracket) > 0) and round_count < max_rounds:
            self.play_upper_bracket(silent)
            self.play_lower_bracket(silent)
            self.play_lower_bracket_with_upper_losers(silent)
            round_count += 1

        if self.grand_finalist and len(self.lower_bracket) == 1:
            self.play_grand_final(silent)

        # Ensure all teams are accounted for in the results
        for team in self.teams:
            if team not in self.results:
                self.results.append(team)

    def play_upper_bracket(self, silent):
        if len(self.upper_bracket) > 1:
            next_round = []
            for i in range(0, len(self.upper_bracket), 2):
                if i + 1 < len(self.upper_bracket):
                    match = Match(self.upper_bracket[i], self.upper_bracket[i+1], best_of=3)
                    result = match.play()
                    self.match_results.append(("Upper Bracket", result))
                    if not silent:
                        self.print_match_result(result)
                    next_round.append(result['winner'])
                    self.upper_bracket_losers.append(result['loser'])
                else:
                    next_round.append(self.upper_bracket[i])
            self.upper_bracket = next_round
        elif len(self.upper_bracket) == 1 and not self.grand_finalist:
            self.grand_finalist = self.upper_bracket.pop()

    def play_lower_bracket(self, silent):
        if len(self.lower_bracket) > 1:
            next_round = []
            for i in range(0, len(self.lower_bracket), 2):
                if i + 1 < len(self.lower_bracket):
                    match = Match(self.lower_bracket[i], self.lower_bracket[i+1], best_of=3)
                    result = match.play()
                    self.match_results.append(("Lower Bracket", result))
                    if not silent:
                        self.print_match_result(result)
                    next_round.append(result['winner'])
                    self.results.insert(0, result['loser'])
                else:
                    next_round.append(self.lower_bracket[i])
            self.lower_bracket = next_round

    def play_lower_bracket_with_upper_losers(self, silent):
        next_round = []
        for i in range(min(len(self.lower_bracket), len(self.upper_bracket_losers))):
            best_of = 5 if len(self.lower_bracket) == 1 and len(self.upper_bracket_losers) == 1 else 3
            match = Match(self.lower_bracket[i], self.upper_bracket_losers[i], best_of=best_of)
            result = match.play()
            self.match_results.append(("Lower Bracket with Upper Losers", result))
            if not silent:
                self.print_match_result(result)
            next_round.append(result['winner'])
            self.results.insert(0, result['loser'])
        
        next_round.extend(self.lower_bracket[len(self.upper_bracket_losers):])
        next_round.extend(self.upper_bracket_losers[len(self.lower_bracket):])
        
        self.lower_bracket = next_round
        self.upper_bracket_losers.clear()

    def play_grand_final(self, silent):
        match = Match(self.grand_finalist, self.lower_bracket[0], best_of=5)
        result = match.play()
        self.match_results.append(("Grand Final", result))
        if not silent:
            print("\nGrand Final:")
            self.print_match_result(result)
        self.results.insert(0, result['loser'])
        self.results.insert(0, result['winner'])

    def print_match_result(self, result):
        home_team = result['home_team']
        away_team = result['away_team']
        print(f"({home_team.rating:.1f}) {home_team.name} {result['home_score']} - {result['away_score']} {away_team.name} ({away_team.rating:.1f})")

    def get_standings(self):
        return self.results

    def display_results(self):
        print("\nPlayoff Results:")
        
        rounds = self.organize_matches_into_rounds()
        
        for round_num, matches in enumerate(rounds, 1):
            print(f"\nRound {round_num}:")
            print("-"*25)
            for round_name, result in matches:
                print(f"{round_name}:")
                self.print_match_result(result)
            print("-"*25)
        
        print("\nFinal Standings:")
        for i, team in enumerate(self.results[:4], 1):
            print(f"{i}. {team.name}")

    def organize_matches_into_rounds(self, matches=None):
        """Organize matches into rounds. If matches is not provided, use self.match_results"""
        if matches is None:
            matches = self.match_results
            
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

    def get_results_text(self):
        """Return formatted tournament results text for storage"""
        text = "Tournament Results:\n"
        text += "-" * 40 + "\n"
        
        # Show all matches by round
        rounds = self.organize_matches_into_rounds(self.match_results)
        for round_num, matches in enumerate(rounds, 1):
            text += f"\nRound {round_num}:\n"
            text += "-" * 25 + "\n"
            for round_name, result in matches:
                text += f"{round_name}:\n"
                text += f"  ({result['home_team'].rating:.1f}) {result['home_team'].name} {result['home_score']} - "
                text += f"{result['away_score']} {result['away_team'].name} ({result['away_team'].rating:.1f})\n"
        
        # Show final standings
        text += "\nFinal Standings:\n"
        text += "-" * 40 + "\n"
        standings = self.get_standings()
        for i, team in enumerate(standings, 1):
            text += f"{i}. {team.name} (Rating: {team.rating:.1f})\n"
        
        return text
