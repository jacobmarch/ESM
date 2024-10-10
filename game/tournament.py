from .match import Match

class DoubleEliminationTournament:
    def __init__(self, teams):
        self.teams = teams
        self.upper_bracket = []
        self.lower_bracket = []
        self.results = []
        self.grand_finalist = None

    def run(self):
        self.upper_bracket = self.teams.copy()
        round_number = 1

        while len(self.upper_bracket) + len(self.lower_bracket) > 1:
            print(f"\nRound {round_number}")
            self.play_upper_bracket()
            self.play_lower_bracket()
            round_number += 1

        # Grand Finals
        if self.grand_finalist and len(self.lower_bracket) == 1:
            print("\nGrand Finals")
            grand_final = Match(self.grand_finalist, self.lower_bracket[0])
            result = grand_final.play()
            print(f"Grand Finals: {result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name}")
            self.results = [result['winner'], result['loser']] + self.results

    def play_upper_bracket(self):
        if len(self.upper_bracket) > 1:
            print("Upper Bracket:")
            next_round = []
            for i in range(0, len(self.upper_bracket), 2):
                if i + 1 < len(self.upper_bracket):
                    match = Match(self.upper_bracket[i], self.upper_bracket[i+1])
                    result = match.play()
                    print(f"{result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name}")
                    next_round.append(result['winner'])
                    self.lower_bracket.append(result['loser'])
                else:
                    next_round.append(self.upper_bracket[i])
            self.upper_bracket = next_round
        elif len(self.upper_bracket) == 1 and not self.grand_finalist:
            self.grand_finalist = self.upper_bracket.pop()

    def play_lower_bracket(self):
        if len(self.lower_bracket) > 1:
            print("Lower Bracket:")
            next_round = []
            for i in range(0, len(self.lower_bracket), 2):
                if i + 1 < len(self.lower_bracket):
                    match = Match(self.lower_bracket[i], self.lower_bracket[i+1])
                    result = match.play()
                    print(f"{result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name}")
                    next_round.append(result['winner'])
                    self.results.insert(0, result['loser'])
                else:
                    next_round.append(self.lower_bracket[i])
            self.lower_bracket = next_round

    def get_standings(self):
        if self.grand_finalist:
            return [self.grand_finalist] + self.results + self.lower_bracket
        return self.results + self.upper_bracket + self.lower_bracket