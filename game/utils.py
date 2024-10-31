import random
import os
import shutil

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

def ensure_results_directory(year):
    """Create results directory structure if it doesn't exist"""
    base_dir = "previous_results"
    year_dir = os.path.join(base_dir, str(year))
    
    # Create base directory if it doesn't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Create year directory if it doesn't exist
    if not os.path.exists(year_dir):
        os.makedirs(year_dir)
    
    return year_dir

def save_results(year, league_name, content):
    """Save results to appropriate file"""
    year_dir = ensure_results_directory(year)
    filename = f"{league_name}_results.txt"
    filepath = os.path.join(year_dir, filename)
    
    # Append mode so we can add results from different phases
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(content + "\n\n")

def clear_previous_results():
    """Clear the previous_results directory if it exists"""
    base_dir = "previous_results"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)