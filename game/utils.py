import random
import os
import shutil
import dotenv
import google.generativeai as genai
from google.generativeai.types import RequestOptions
from google.api_core import retry
import json

# Load environment variables and configure AI
dotenv.load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro-002')

def generate_yearly_summary(year):
    """Generate an AI summary of the year's results"""
    # Get all results for the year
    year_dir = os.path.join("previous_results", str(year))
    if not os.path.exists(year_dir):
        return None
    
    # Read all result files
    results_data = {}
    for filename in os.listdir(year_dir):
        if filename.endswith("_results.txt"):
            with open(os.path.join(year_dir, filename), 'r', encoding='utf-8') as f:
                results_data[filename] = f.read()
    
    # Try to get previous year's summary if it exists
    previous_year = year - 1
    previous_summary = ""
    previous_year_dir = os.path.join("previous_results", str(previous_year))
    previous_summary_path = os.path.join(previous_year_dir, "yearly_summary.md")
    if os.path.exists(previous_summary_path):
        with open(previous_summary_path, 'r', encoding='utf-8') as f:
            previous_summary = f.read()
    
    # Create prompt for AI
    context_message = f"Here is the previous year's summary for context and continuity:\n{previous_summary}" if previous_summary else "This is the first year of the competition."
    
    prompt = f"""
    You are a professional esports journalist. Based on the following competition results from {year}, 
    create a comprehensive yearly summary with the following sections:
    1. Major Headlines from Preseason (2-3 attention-grabbing headlines regarding expectations and predictions)
    2. Top Players (Top players heading into the season across all regions)
    3. Regular Season Highlights (key storylines from each region)
    4. Playoff Predictions (predictions for the playoffs based on the regular season results)
    5. Playoff Drama (most exciting moments and upsets)
    6. Playoff Summaries (detailed analysis of the playoffs)
    7. World Championship Review (detailed analysis of the tournament)
    
    Format the response as a newspaper-style article with clear section headers.
    Keep the tone engaging and focus on the most key stories and topics for each section of the article.
    
    {context_message}
    
    Here are the results to analyze:
    """
    
    try:
        # Generate AI response
        response = model.generate_content(
            prompt + json.dumps(results_data),
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40
            },
            request_options=RequestOptions(
                retry=retry.Retry(
                    initial=10,
                    multiplier=2,
                    maximum=60,
                    timeout=300
                )
            )
        )
        
        # Save the summary
        summary_path = os.path.join(year_dir, "yearly_summary.md")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        return response.text
        
    except Exception as e:
        print(f"Error generating summary for year {year}: {str(e)}")
        return None

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
    """Save results to appropriate file and generate summary if it's the World Championship"""
    year_dir = ensure_results_directory(year)
    filename = f"{league_name}_results.txt"
    filepath = os.path.join(year_dir, filename)
    
    # Append mode so we can add results from different phases
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(content + "\n\n")
    
    # Generate yearly summary after World Championship results are saved
    if league_name == "World_Championship":
        generate_yearly_summary(year)

def clear_previous_results():
    """Clear the previous_results directory if it exists"""
    base_dir = "previous_results"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)