import random
import os

def load_data(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'data', filename)
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip() and not line.strip().startswith('[')]

def load_team_names():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'data', 'team_names.txt')
    team_names = {}
    current_region = None
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                current_region = line[1:-1]
                team_names[current_region] = []
            elif line and current_region:
                team_names[current_region].append(line)
    return team_names

def get_random_name(first_names, last_names):
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def get_random_gamer_tag(gamer_tags):
    return random.choice(gamer_tags)

def get_random_team_name(team_names):
    region = random.choice(list(team_names.keys()))
    return random.choice(team_names[region])