import random
from .match import Match
from .tournament import DoubleEliminationTournament

class Season:
    def __init__(self, teams, current_year):
        self.teams = teams
        self.current_year = current_year
        self.matches = []
        # Track wins, losses, map wins, map losses for each team
        self.standings = {team: {'wins': 0, 'losses': 0, 'map_wins': 0, 'map_losses': 0} for team in teams}
        # Track head-to-head results
        self.head_to_head = {team: {other: 0 for other in teams if other != team} for team in teams}

    def run_regular_season(self):
        # Create a list of all possible matchups
        matchups = []
        for i, team1 in enumerate(self.teams):
            for team2 in self.teams[i+1:]:  # Only match with teams not yet played
                # Randomly determine home/away
                if random.random() < 0.5:
                    matchups.append((team1, team2))
                else:
                    matchups.append((team2, team1))
        
        # Shuffle the matchups for variety
        random.shuffle(matchups)
        
        # Play all matches
        for home_team, away_team in matchups:
            match = Match(home_team, away_team, match_type='R', current_year=self.current_year)
            result = match.play()
            self.update_standings(result)
            self.matches.append(match)

    def update_standings(self, result):
        winner = result['winner']
        loser = result['loser']
        home_team = result['home_team']
        away_team = result['away_team']
        
        # Update match record
        self.standings[winner]['wins'] += 1
        self.standings[loser]['losses'] += 1
        
        # Update map record
        self.standings[home_team]['map_wins'] += result['home_score']
        self.standings[home_team]['map_losses'] += result['away_score']
        self.standings[away_team]['map_wins'] += result['away_score']
        self.standings[away_team]['map_losses'] += result['home_score']
        
        # Update head-to-head
        if winner == home_team:
            self.head_to_head[home_team][away_team] += 1
        else:
            self.head_to_head[away_team][home_team] += 1

    def get_map_differential(self, team):
        stats = self.standings[team]
        return stats['map_wins'] - stats['map_losses']

    def get_round_differential(self, team):
        """Calculate round differential for a team across all matches."""
        total_rounds_won = 0
        total_rounds_lost = 0
        
        for match in self.matches:
            result = match.play()
            if result['home_team'] == team or result['away_team'] == team:
                for game in result['games']:
                    for round_info in game['rounds']:
                        if round_info['winner'] == team:
                            total_rounds_won += 1
                        else:
                            total_rounds_lost += 1

        return total_rounds_won - total_rounds_lost

    def resolve_tiebreaker(self, tied_teams):
        if len(tied_teams) == 2:
            team1, team2 = tied_teams
            if self.head_to_head[team1][team2] > self.head_to_head[team2][team1]:
                return [team1, team2]
            elif self.head_to_head[team2][team1] > self.head_to_head[team1][team2]:
                return [team2, team1]
        
        # Sort by map differential
        map_diff_sorted = sorted(tied_teams, 
                               key=lambda t: self.get_map_differential(t),
                               reverse=True)
        
        # Check if map differential resolved the tie
        map_diffs = [self.get_map_differential(team) for team in map_diff_sorted]
        if len(set(map_diffs)) == len(map_diffs):
            return map_diff_sorted
            
        # Group teams that are still tied after map differential
        still_tied = []
        current_group = []
        current_diff = None
        
        for team, diff in zip(map_diff_sorted, map_diffs):
            if diff != current_diff:
                if len(current_group) > 1:
                    still_tied.extend(self.resolve_tiebreaker_by_rounds(current_group))
                else:
                    still_tied.extend(current_group)
                current_group = [team]
                current_diff = diff
            else:
                current_group.append(team)
                
        if current_group:
            if len(current_group) > 1:
                still_tied.extend(self.resolve_tiebreaker_by_rounds(current_group))
            else:
                still_tied.extend(current_group)
                
        return still_tied

    def resolve_tiebreaker_by_rounds(self, tied_teams):
        # Sort by round differential
        round_diff_sorted = sorted(tied_teams,
                                 key=lambda t: self.get_round_differential(t),
                                 reverse=True)
        
        # If still tied, randomize the remaining teams
        round_diffs = [self.get_round_differential(team) for team in round_diff_sorted]
        if len(set(round_diffs)) != len(round_diffs):
            import random
            random.shuffle(round_diff_sorted)
            
        return round_diff_sorted

    def get_standings(self):
        # First sort by win-loss record
        teams_by_record = sorted(self.teams,
                               key=lambda t: (self.standings[t]['wins'], -self.standings[t]['losses']),
                               reverse=True)
        
        # Group teams with same record
        final_standings = []
        current_group = []
        current_record = None
        
        for team in teams_by_record:
            record = (self.standings[team]['wins'], self.standings[team]['losses'])
            if record != current_record:
                if len(current_group) > 1:
                    final_standings.extend(self.resolve_tiebreaker(current_group))
                else:
                    final_standings.extend(current_group)
                current_group = [team]
                current_record = record
            else:
                current_group.append(team)
                
        if current_group:
            if len(current_group) > 1:
                final_standings.extend(self.resolve_tiebreaker(current_group))
            else:
                final_standings.extend(current_group)
                
        return final_standings

    def get_standings_text(self):
        """Return formatted standings text for storage"""
        standings = self.get_standings()
        text = "Regular Season Standings:\n"
        text += "-" * 40 + "\n"
        
        for i, team in enumerate(standings, 1):
            stats = self.standings[team]
            text += f"{i}. {team.name:<20} {stats['wins']}-{stats['losses']} ({stats['map_wins']}-{stats['map_losses']})\n"
        
        # Update match results section
        text += "\nMatch Results:\n"
        text += "-" * 40 + "\n"
        for match in self.matches:
            result = match.play()
            text += f"({result['home_team'].rating:.1f}) {result['home_team'].name} {result['home_score']} - {result['away_score']} {result['away_team'].name} ({result['away_team'].rating:.1f})\n"
            
            # Calculate map differentials
            map_differentials = {
                map_name: match._calculate_map_scores(result['home_team'], result['away_team'])[map_name] - 
                         match._calculate_map_scores(result['away_team'], result['home_team'])[map_name]
                for map_name in match.available_maps
            }
            
            # Add map sequence with differentials
            text += "Map Sequence:\n"
            for action, team, map_name in result['map_sequence']:
                if action == 'decider':
                    text += f"     Decider: {map_name} (Diff: {map_differentials[map_name]:+d})\n"
                else:
                    # Show differential from the picking team's perspective
                    diff = map_differentials[map_name] if team == result['home_team'] else -map_differentials[map_name]
                    text += f"     {team.name} {action}: {map_name} (Diff: {diff:+d})\n"
            
            # Add individual map scores
            for game in result['games']:
                home_score, away_score = game['score']
                text += f"     {game['map']}: {home_score}-{away_score}\n"
            text += "\n"
        
        return text

    def print_standings(self):
        standings = self.get_standings()
        print("\nStandings:")
        for i, team in enumerate(standings, 1):
            stats = self.standings[team]
            print(f"{i}. {team.name:<20} {stats['wins']}-{stats['losses']} ({stats['map_wins']}-{stats['map_losses']})")
        print()

    def run_playoffs(self, league_name):
        print(f"\n{league_name} Playoffs:")
        top_teams = self.get_top_teams(8)  # Get top 8 teams for playoffs
        tournament = DoubleEliminationTournament(
            teams=top_teams, 
            match_type='P',
            current_year=self.current_year  # Pass current_year to tournament
        )
        tournament.run()
        final_standings = tournament.get_standings()
        
        print(f"\n{league_name} Playoff Results:")
        for i, team in enumerate(final_standings[:4], 1):
            print(f"{i}. {team.name}")

        return final_standings[:4]

    def get_top_teams(self, count):
        """Get top N teams based on standings"""
        standings = self.get_standings()
        return standings[:count]
