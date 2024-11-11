import random
from .team import Team
from .player import Player
import os
from datetime import datetime

class Match:
    def __init__(self, home_team: Team, away_team: Team, best_of=3, upper_loser=None, match_type='R', current_year=None):
        self.home_team = home_team
        self.away_team = away_team
        self.best_of = best_of
        self.result = None
        self.available_maps = Player.MAPS.copy()  # Use maps from Player class
        self.upper_loser = upper_loser  # Track which team came from upper bracket
        self.match_type = match_type
        self.current_year = current_year

    def _calculate_map_scores(self, team: Team, opponent: Team) -> dict:
        """Calculate strategic scores for each map based on team strengths/weaknesses."""
        map_scores = {map_name: 0 for map_name in self.available_maps}
        
        # Evaluate own team's strengths/weaknesses
        for player in team.players:
            for map_name in self.available_maps:
                modifier = player.get_map_skill_modifier(map_name)
                if modifier > 0:
                    map_scores[map_name] += 2
                elif modifier < 0:
                    map_scores[map_name] -= 2
        
        # Evaluate opponent's strengths/weaknesses
        for player in opponent.players:
            for map_name in self.available_maps:
                modifier = player.get_map_skill_modifier(map_name)
                if modifier > 0:
                    map_scores[map_name] -= 1
                elif modifier < 0:
                    map_scores[map_name] += 1
                    
        return map_scores

    def _get_best_map(self, available_maps: list, map_scores: dict) -> str:
        """Return the map with the highest score from available maps."""
        return max(available_maps, key=lambda m: map_scores[m])

    def _get_worst_map(self, available_maps: list, map_scores: dict) -> str:
        """Return the map with the lowest score from available maps."""
        return min(available_maps, key=lambda m: map_scores[m])

    def _pick_ban_maps(self):
        """Handle map pick/ban phase based on match format."""
        available_maps = self.available_maps.copy()
        map_sequence = []
        
        # Calculate base map scores for both teams
        home_map_scores = self._calculate_map_scores(self.home_team, self.away_team)
        away_map_scores = self._calculate_map_scores(self.away_team, self.home_team)
        
        # Calculate differential scores (home perspective)
        map_differentials = {
            map_name: home_map_scores[map_name] - away_map_scores[map_name]
            for map_name in available_maps
        }

        def _get_best_differential_map(maps, team_is_home):
            """Returns map with highest differential for given team"""
            diffs = {m: (map_differentials[m] if team_is_home else -map_differentials[m]) 
                    for m in maps}
            return max(diffs.items(), key=lambda x: x[1])[0]
        
        def _get_worst_differential_map(maps, team_is_home):
            """Returns map with lowest differential for given team"""
            diffs = {m: (map_differentials[m] if team_is_home else -map_differentials[m]) 
                    for m in maps}
            return min(diffs.items(), key=lambda x: x[1])[0]

        if self.best_of == 3:
            # Team A Ban (map where they're at biggest disadvantage)
            map1 = _get_worst_differential_map(available_maps, True)
            available_maps.remove(map1)
            map_sequence.append(('ban', self.home_team, map1))

            # Team B Ban (map where they're at biggest disadvantage)
            map2 = _get_worst_differential_map(available_maps, False)
            available_maps.remove(map2)
            map_sequence.append(('ban', self.away_team, map2))

            # Team A Pick (map where they have biggest advantage)
            map3 = _get_best_differential_map(available_maps, True)
            available_maps.remove(map3)
            map_sequence.append(('pick', self.home_team, map3))

            # Team B Pick (map where they have biggest advantage)
            map4 = _get_best_differential_map(available_maps, False)
            available_maps.remove(map4)
            map_sequence.append(('pick', self.away_team, map4))

            # Continue with remaining bans using differential
            map5 = _get_worst_differential_map(available_maps, True)
            available_maps.remove(map5)
            map_sequence.append(('ban', self.home_team, map5))

            map6 = _get_worst_differential_map(available_maps, False)
            available_maps.remove(map6)
            map_sequence.append(('ban', self.away_team, map6))

            # Final Map
            map7 = available_maps[0]
            map_sequence.append(('decider', None, map7))

            return [map3, map4, map7], map_sequence

        else:  # best_of == 5
            upper_loser_team = self.upper_loser if self.upper_loser else self.home_team
            upper_loser_is_home = upper_loser_team == self.home_team

            # Upper bracket loser bans twice (maps where they're at biggest disadvantage)
            map1 = _get_worst_differential_map(available_maps, upper_loser_is_home)
            available_maps.remove(map1)
            map_sequence.append(('ban', upper_loser_team, map1))

            map2 = _get_worst_differential_map(available_maps, upper_loser_is_home)
            available_maps.remove(map2)
            map_sequence.append(('ban', upper_loser_team, map2))

            # Upper bracket loser picks Map 1 (biggest advantage)
            map3 = _get_best_differential_map(available_maps, upper_loser_is_home)
            available_maps.remove(map3)
            map_sequence.append(('pick', upper_loser_team, map3))

            # Other team picks Map 2
            map4 = _get_best_differential_map(available_maps, not upper_loser_is_home)
            available_maps.remove(map4)
            map_sequence.append(('pick', self.away_team if upper_loser_is_home else self.home_team, map4))

            # Upper bracket loser picks Map 3
            map5 = _get_best_differential_map(available_maps, upper_loser_is_home)
            available_maps.remove(map5)
            map_sequence.append(('pick', upper_loser_team, map5))

            # Other team picks Map 4
            map6 = _get_best_differential_map(available_maps, not upper_loser_is_home)
            available_maps.remove(map6)
            map_sequence.append(('pick', self.away_team if upper_loser_is_home else self.home_team, map6))

            # Final Map
            map7 = available_maps[0]
            map_sequence.append(('decider', None, map7))

            return [map3, map4, map5, map6, map7], map_sequence

    def play(self):
        if self.result:
            return self.result
            
        maps_to_play, map_sequence = self._pick_ban_maps()
        home_wins = 0
        away_wins = 0
        games_to_win = (self.best_of // 2) + 1
        games_played = []

        for current_map in maps_to_play:
            if home_wins < games_to_win and away_wins < games_to_win:
                home_score, away_score, round_details = self.simulate_game(current_map)
                games_played.append({
                    'map': current_map,
                    'score': (home_score, away_score),
                    'rounds': round_details
                })

                if home_score > away_score:
                    home_wins += 1
                else:
                    away_wins += 1

        winner = self.home_team if home_wins > away_wins else self.away_team
        loser = self.away_team if home_wins > away_wins else self.home_team

        self.result = {
            'home_team': self.home_team,
            'away_team': self.away_team,
            'home_score': home_wins,
            'away_score': away_wins,
            'winner': winner,
            'loser': loser,
            'games': games_played,
            'map_sequence': map_sequence
        }
        return self.result

    def _create_stats_file(self, region):
        """Create directory structure and return file path for match statistics."""
        # Ensure we have a valid current_year
        if not self.current_year:
            raise ValueError("current_year must be set for match statistics")
            
        # For World Championship matches, use a special folder
        if self.match_type in ['G', 'K']:
            base_path = f"previous_results/{self.current_year}/World_Championship"
        else:
            base_path = f"previous_results/{self.current_year}/{region}"
            
        os.makedirs(base_path, exist_ok=True)
        
        # For World Championship matches, add stage information to filename
        if self.match_type == 'G':
            filename = f"{self.home_team.name}_{self.away_team.name}_Group.txt"
        elif self.match_type == 'K':
            filename = f"{self.home_team.name}_{self.away_team.name}_Knockout.txt"
        else:
            filename = f"{self.home_team.name}_{self.away_team.name}_{self.match_type}.txt"
            
        return os.path.join(base_path, filename)
        
    def _write_map_stats(self, filepath, map_name, map_stats):
        """Write statistics for a single map to the file."""
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"\nMap: {map_name}\n")
            f.write("-" * 13 + "\n")
            
            # Write home team stats
            f.write(f"{self.home_team.name}\n")
            f.write("-" * 13 + "\n")
            f.write("Player Name, K, D, A\n")
            for player, stats in map_stats['home_team'].items():
                f.write(f"{player}, {stats['K']}, {stats['D']}, {stats['A']}\n")
            
            f.write("\n")
            
            # Write away team stats
            f.write(f"{self.away_team.name}\n")
            f.write("-" * 13 + "\n")
            f.write("Player Name, K, D, A\n")
            for player, stats in map_stats['away_team'].items():
                f.write(f"{player}, {stats['K']}, {stats['D']}, {stats['A']}\n")
            
            f.write("\n" + "=" * 30 + "\n")

    def simulate_game(self, current_map):
        home_score = 0
        away_score = 0
        round_details = []
        
        # Initialize map statistics
        map_stats = {
            'home_team': {player: {'K': 0, 'D': 0, 'A': 0} for player in self.home_team.players},
            'away_team': {player: {'K': 0, 'D': 0, 'A': 0} for player in self.away_team.players}
        }

        while home_score < 13 and away_score < 13:
            round_winner, round_info = self.simulate_round(current_map)
            round_details.append(round_info)
            
            # Update statistics based on round results
            self._update_stats(round_info, map_stats)
            
            if round_winner == self.home_team:
                home_score += 1
            else:
                away_score += 1

            if home_score == 12 and away_score == 12:
                while abs(home_score - away_score) < 2:
                    round_winner, round_info = self.simulate_round(current_map)
                    round_details.append(round_info)
                    self._update_stats(round_info, map_stats)
                    if round_winner == self.home_team:
                        home_score += 1
                    else:
                        away_score += 1

        # Write map statistics to file
        stats_file = self._create_stats_file(self.home_team.region)
        self._write_map_stats(stats_file, current_map, map_stats)

        return home_score, away_score, round_details

    def _update_stats(self, round_info, map_stats):
        """Update map statistics based on round results."""
        for encounter in round_info['encounters']:
            # Select one winner to get the kills (first player in winners list)
            if encounter['winners']:
                killer = encounter['winners'][0]
                team_key = 'home_team' if killer in self.home_team.players else 'away_team'
                # Award kills only to the primary killer
                map_stats[team_key][killer]['K'] += len(encounter['losers'])
            
            # Update deaths for losers
            for loser in encounter['losers']:
                team_key = 'home_team' if loser in self.home_team.players else 'away_team'
                map_stats[team_key][loser]['D'] += 1
            
            # Update assists for other winners
            for winner in encounter['winners'][1:]:  # Skip the killer, only process potential assisters
                team_key = 'home_team' if winner in self.home_team.players else 'away_team'
                if random.random() < 0.35:  # 35% chance for assist
                    map_stats[team_key][winner]['A'] += len(encounter['losers'])

    def simulate_round(self, current_map):
        home_alive = self.home_team.players.copy()
        away_alive = self.away_team.players.copy()
        encounters = []

        while home_alive and away_alive:
            # Determine group sizes based on available players
            max_group_size = min(3, len(home_alive), len(away_alive))
            home_group_size = random.randint(1, max_group_size)
            away_group_size = random.randint(1, max_group_size)
            
            # Select random players for each group
            home_group = random.sample(home_alive, home_group_size)
            away_group = random.sample(away_alive, away_group_size)
            
            winners, losers = self.simulate_group_encounter(home_group, away_group, current_map)
            encounters.append(({
                'home_group': home_group,
                'away_group': away_group,
                'winners': winners,
                'losers': losers
            }))
            
            # Remove eliminated players
            for loser in losers:
                if loser in home_alive:
                    home_alive.remove(loser)
                else:
                    away_alive.remove(loser)

        round_winner = self.home_team if home_alive else self.away_team
        round_info = {
            'winner': round_winner,
            'encounters': encounters,
            'last_standing': home_alive if round_winner == self.home_team else away_alive,
            'map': current_map
        }
        return round_winner, round_info

    def simulate_group_encounter(self, home_group: list, away_group: list, current_map: str):
        """Simulate an encounter between two groups of players."""
        # Calculate numerical advantage bonus (0.1 per player advantage)
        number_advantage = (len(home_group) - len(away_group)) * 0.1
        
        # Calculate total effective skill for each group
        home_skill = sum(p.skill + p.get_map_skill_modifier(current_map) for p in home_group)
        away_skill = sum(p.skill + p.get_map_skill_modifier(current_map) for p in away_group)
        
        # Apply numerical advantage bonus
        if number_advantage > 0:
            home_skill *= (1 + number_advantage)
        elif number_advantage < 0:
            away_skill *= (1 + abs(number_advantage))
        
        # Calculate win probability
        total_skill = home_skill + away_skill
        home_win_prob = home_skill / total_skill
        home_win_prob = max(0.1, min(0.9, home_win_prob))  # Clamp between 0.1 and 0.9
        
        if random.random() < home_win_prob:
            return home_group, away_group
        else:
            return away_group, home_group

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"
