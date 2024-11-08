import random
from .utils import get_random_name, get_random_gamer_tag, load_data
import numpy as np

class Player:
    first_names = load_data('first_names.txt')
    last_names = load_data('last_names.txt')
    gamer_tags = load_data('gamer_tags.txt')

    # Add available maps as class variable
    MAPS = ['Split', 'Haven', 'Bind', 'Abyss', 'Ascent', 'Icebox', 'Lotus']

    @staticmethod
    def generate_skill():
        # Use a normal distribution with mean 75 and standard deviation 10
        skill = int(np.random.normal(75, 10))
        # Clamp the skill between 50 and 100
        return max(50, min(100, skill))

    def __init__(self):
        self.first_name, self.last_name = get_random_name(self.first_names, self.last_names).split()
        self.gamer_tag = get_random_gamer_tag(self.gamer_tags)
        self.skill = self.generate_skill()
        self.contract_length = random.choice([1, 2, 3])
        self.contract_years_left = self.contract_length

        # Initialize map preferences
        self.good_maps, self.bad_maps = self._assign_map_preferences()

    def _assign_map_preferences(self):
        """Assign map preferences based on player skill."""
        maps = self.MAPS.copy()
        random.shuffle(maps)
        
        # Calculate number of bad maps based on skill
        # Higher skill = fewer bad maps
        max_bad_maps = max(1, min(3, int((100 - self.skill) / 20)))
        num_bad_maps = random.randint(1, max_bad_maps)
        
        # Always have at least one good map
        num_good_maps = random.randint(1, 3)
        
        good_maps = set(maps[:num_good_maps])
        remaining_maps = set(maps[num_good_maps:])
        bad_maps = set(random.sample(list(remaining_maps), num_bad_maps))
        
        return good_maps, bad_maps

    @property
    def neutral_maps(self):
        """Return maps that are neither good nor bad."""
        return set(self.MAPS) - (self.good_maps | self.bad_maps)

    def get_map_skill_modifier(self, map_name):
        """Return skill modifier for a given map."""
        if map_name in self.good_maps:
            return 10  # +10 skill on good maps
        elif map_name in self.bad_maps:
            return -10  # -10 skill on bad maps
        return 0  # no modifier for neutral maps

    def improve(self):
        # Slight improvement with a small chance of a bigger jump
        improvement = random.choices([0, 1, 2, 3], weights=[0.4, 0.3, 0.2, 0.1])[0]
        self.skill = min(100, self.skill + improvement)

    def decrease_contract_length(self):
        self.contract_years_left -= 1

    def renew_contract(self):
        self.contract_length = random.choice([1, 2, 3])
        self.contract_years_left = self.contract_length

    def __str__(self):
        return f"{self.first_name} \"{self.gamer_tag}\" {self.last_name} (Skill: {self.skill})"

    def __repr__(self):
        return self.__str__()