import random
from .utils import get_random_name, get_random_gamer_tag, load_data

class Player:
    first_names = load_data('first_names.txt')
    last_names = load_data('last_names.txt')
    gamer_tags = load_data('gamer_tags.txt')

    def __init__(self):
        self.first_name, self.last_name = get_random_name(self.first_names, self.last_names).split()
        self.gamer_tag = get_random_gamer_tag(self.gamer_tags)
        self.skill = random.randint(50, 100)
        self.contract_length = random.choice([1, 2, 3])
        self.contract_years_left = self.contract_length

    def improve(self):
        self.skill = min(100, self.skill + random.randint(0, 5))

    def decrease_contract_length(self):
        self.contract_years_left -= 1

    def renew_contract(self):
        self.contract_length = random.choice([1, 2, 3])
        self.contract_years_left = self.contract_length

    def __str__(self):
        return f"{self.first_name} \"{self.gamer_tag}\" {self.last_name}"

    def __repr__(self):
        return self.__str__()