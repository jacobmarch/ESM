import random
from .team import Team
from .player import Player

class Match:
    def __init__(self, home_team: Team, away_team: Team, best_of=3, upper_loser=None):
        self.home_team = home_team
        self.away_team = away_team
        self.best_of = best_of
        self.result = None
        self.available_maps = Player.MAPS.copy()  # Use maps from Player class
        self.upper_loser = upper_loser  # Track which team came from upper bracket

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

    def simulate_game(self, current_map):
        home_score = 0
        away_score = 0
        round_details = []

        while home_score < 13 and away_score < 13:
            round_winner, round_info = self.simulate_round(current_map)
            round_details.append(round_info)
            if round_winner == self.home_team:
                home_score += 1
            else:
                away_score += 1

            if home_score == 12 and away_score == 12:
                while abs(home_score - away_score) < 2:
                    round_winner, round_info = self.simulate_round(current_map)
                    round_details.append(round_info)
                    if round_winner == self.home_team:
                        home_score += 1
                    else:
                        away_score += 1

        return home_score, away_score, round_details

    def simulate_round(self, current_map):
        home_alive = self.home_team.players.copy()
        away_alive = self.away_team.players.copy()
        encounters = []

        while home_alive and away_alive:
            home_player = random.choice(home_alive)
            away_player = random.choice(away_alive)

            winner, loser = self.simulate_encounter(home_player, away_player, current_map)
            encounters.append((winner, loser))

            if winner in home_alive:
                away_alive.remove(loser)
            else:
                home_alive.remove(loser)

        round_winner = self.home_team if home_alive else self.away_team
        round_info = {
            'winner': round_winner,
            'encounters': encounters,
            'last_standing': home_alive if round_winner == self.home_team else away_alive,
            'map': current_map
        }
        return round_winner, round_info

    def simulate_encounter(self, player1: Player, player2: Player, current_map):
        # Apply map-specific skill modifiers
        player1_skill = player1.skill + player1.get_map_skill_modifier(current_map)
        player2_skill = player2.skill + player2.get_map_skill_modifier(current_map)
        
        skill_diff = player1_skill - player2_skill
        win_probability = 0.5 + (skill_diff / 200)
        win_probability = max(0.1, min(0.9, win_probability))

        if random.random() < win_probability:
            return player1, player2
        else:
            return player2, player1

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"
