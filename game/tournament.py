from .match import Match

class DoubleEliminationTournament:
    def __init__(self, teams):
        self.teams = teams
        self.upper_bracket = teams.copy()
        self.lower_bracket = []
        self.upper_bracket_losers = []
        self.results = []
        self.grand_finalist = None
        self.champion = None
        self.round_number = 0

    def run(self):
        while len(self.upper_bracket) + len(self.lower_bracket) > 1:
            self.round_number += 1
            print(f"\nRound {self.round_number}")
            self.play_upper_bracket()
            
            if self.round_number == 1:
                # After first round, losers go directly to lower bracket
                self.lower_bracket.extend(self.upper_bracket_losers)
                self.upper_bracket_losers.clear()
            elif self.upper_bracket_losers:
                self.play_lower_bracket_with_upper_losers()
            
            self.play_lower_bracket()

        # Grand Finals (Best of 5)
        if self.grand_finalist and len(self.lower_bracket) == 1:
            print("\nGrand Finals (Best of 5)")
            grand_final = Match(self.grand_finalist, self.lower_bracket[0], best_of=5)
            result = grand_final.play()
            self.print_match_result(result)
            self.champion = result['winner']
            self.results.insert(0, result['loser'])

    def play_upper_bracket(self):
        if len(self.upper_bracket) > 1:
            print("Upper Bracket (Best of 3):")
            next_round = []
            for i in range(0, len(self.upper_bracket), 2):
                if i + 1 < len(self.upper_bracket):
                    match = Match(self.upper_bracket[i], self.upper_bracket[i+1], best_of=3)
                    result = match.play()
                    self.print_match_result(result)
                    next_round.append(result['winner'])
                    self.upper_bracket_losers.append(result['loser'])
                else:
                    next_round.append(self.upper_bracket[i])
            self.upper_bracket = next_round
        elif len(self.upper_bracket) == 1 and not self.grand_finalist:
            self.grand_finalist = self.upper_bracket.pop()

    def play_lower_bracket_with_upper_losers(self):
        print("Lower Bracket with Upper Bracket Losers:")
        next_round = []
        for i in range(min(len(self.lower_bracket), len(self.upper_bracket_losers))):
            best_of = 5 if len(self.lower_bracket) == 1 and len(self.upper_bracket_losers) == 1 else 3
            match = Match(self.lower_bracket[i], self.upper_bracket_losers[i], best_of=best_of)
            result = match.play()
            self.print_match_result(result)
            next_round.append(result['winner'])
            self.results.insert(0, result['loser'])
        
        # Add any remaining teams to next_round
        next_round.extend(self.lower_bracket[len(self.upper_bracket_losers):])
        next_round.extend(self.upper_bracket_losers[len(self.lower_bracket):])
        
        self.lower_bracket = next_round
        self.upper_bracket_losers.clear()

    def play_lower_bracket(self):
        if len(self.lower_bracket) > 1:
            print("Lower Bracket:")
            next_round = []
            for i in range(0, len(self.lower_bracket), 2):
                if i + 1 < len(self.lower_bracket):
                    best_of = 5 if len(self.lower_bracket) == 2 and self.grand_finalist else 3
                    match = Match(self.lower_bracket[i], self.lower_bracket[i+1], best_of=best_of)
                    result = match.play()
                    self.print_match_result(result)
                    next_round.append(result['winner'])
                    self.results.insert(0, result['loser'])
                else:
                    next_round.append(self.lower_bracket[i])
            self.lower_bracket = next_round

    def get_standings(self):
        if self.champion:
            return [self.champion] + [self.results[0]] + self.results[1:]
        elif self.grand_finalist:
            return [self.grand_finalist] + self.lower_bracket + self.results
        return self.upper_bracket + self.lower_bracket + self.results

    def print_match_result(self, result):
        print(f"{'(Best of 5)' if result['home_score'] + result['away_score'] > 3 else '(Best of 3)'} "
              f"{result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name}")
        for i, (home_score, away_score) in enumerate(result['games'], 1):
            print(f"  Game {i}: {result['home_team'].name} {home_score} - {away_score} {result['away_team'].name}")
        print(f"  Winner: {result['winner'].name}")
