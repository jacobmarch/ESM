import random
from .utils import get_random_name, get_random_gamer_tag, load_data

class Player:
    first_names = load_data('first_names.txt')
    last_names = load_data('last_names.txt')
    gamer_tags = load_data('gamer_tags.txt')

    def __init__(self):
        self.name = get_random_name(self.first_names, self.last_names)
        self.gamer_tag = get_random_gamer_tag(self.gamer_tags)
        self.skill = random.randint(50, 100)

    def improve(self):
        self.skill = min(100, self.skill + random.randint(0, 5))

    def __str__(self):
        return f"{self.name} ({self.gamer_tag})"