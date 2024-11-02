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

def get_relevant_results(results_data, section_name):
    """Extract relevant portions of results data based on the article section"""
    relevant_data = {}
    
    for filename, content in results_data.items():
        sections = content.split("\n\n\n")  # Split by triple newline to separate major sections
        
        if section_name in ["preseason_preview", "player_spotlight"]:
            # Only include Off-Season and Preseason sections
            relevant_sections = [section for section in sections 
                               if "Off-Season Results" in section 
                               or "Preseason Preview" in section]
            
        elif section_name in ["regular_season_recap", "playoff_preview"]:
            # Include everything up through Regular Season
            relevant_sections = [section for section in sections 
                               if "Off-Season Results" in section 
                               or "Preseason Preview" in section
                               or "Regular Season Results" in section]
            
        elif section_name in ["playoff_drama", "playoff_analysis"]:
            # Include everything up through Playoffs
            relevant_sections = [section for section in sections 
                               if "Off-Season Results" in section 
                               or "Preseason Preview" in section
                               or "Regular Season Results" in section
                               or "Playoff Results" in section]
            
        else:  # worlds_preview and worlds_recap
            # Include all sections
            relevant_sections = sections
            
        if relevant_sections:
            relevant_data[filename] = "\n\n\n".join(relevant_sections)
    
    return relevant_data

def generate_yearly_summary(year):
    """Generate a collection of AI-written articles summarizing different aspects of the year"""
    year_dir = os.path.join("previous_results", str(year))
    if not os.path.exists(year_dir):
        return None
    
    # Read all result files
    results_data = {}
    for filename in os.listdir(year_dir):
        if filename.endswith("_results.txt"):
            with open(os.path.join(year_dir, filename), 'r', encoding='utf-8') as f:
                results_data[filename] = f.read()
    
    # Get previous year's summary
    previous_year = year - 1
    previous_summary = ""
    previous_year_dir = os.path.join("previous_results", str(previous_year))
    previous_summary_path = os.path.join(previous_year_dir, "yearly_summary.md")
    if os.path.exists(previous_summary_path):
        with open(previous_summary_path, 'r', encoding='utf-8') as f:
            previous_summary = f.read()

    flash_model = genai.GenerativeModel('gemini-1.5-flash-002')
    
    # Add journalist persona
    journalist_persona = """You are Dave Carrington, a veteran journalist assigned to cover the Valorant Champions Tour. You are known for:
    - Your professional writing style
    - Analyzing the results and offseason events to provide context for the upcoming season
    - Thoroughly explaining your thought process when providing opinions and predictions
    Write in your authentic voice while maintaining journalistic integrity."""

    section_prompts = {
        "preseason_preview": f"""{journalist_persona}
            Write a complete news article about preseason expectations for {year}.
            Include 2-3 attention-grabbing headlines and focus on team/player predictions.
            Format as a standalone news article with a title, date ({year}-01-15), and journalist byline.""",
            
        "player_spotlight": f"""{journalist_persona}
            Write a complete news article analyzing the top players heading into {year}.
            Focus on their previous achievements and expectations.
            Format as a standalone news article with a title, date ({year}-02-01), and journalist byline.""",
            
        "regular_season_recap": f"""{journalist_persona}
            Write a complete news article covering the key storylines from the {year} regular season.
            Include regional highlights and standout performances.
            Format as a standalone news article with a title, date ({year}-06-15), and journalist byline.""",
            
        "playoff_preview": f"""{journalist_persona}
            Write a complete news article previewing the {year} playoffs.
            Include predictions and key matchups to watch.
            Format as a standalone news article with a title, date ({year}-08-01), and journalist byline.""",
            
        "playoff_analysis": f"""{journalist_persona}
            Write a complete news article analyzing the {year} playoff results.
            Compare the actual results to pre-playoff predictions, highlight dramatic moments and upsets,
            and provide detailed breakdowns of winning strategies and team performances.
            Format as a standalone news article with a title, date ({year}-08-20), and journalist byline.""",
            
        "worlds_preview": f"""{journalist_persona}
            Write a complete news article previewing the {year} World Championship.
            Include predictions and teams to watch.
            Format as a standalone news article with a title, date ({year}-10-10), and journalist byline.""",
            
        "worlds_recap": f"""{journalist_persona}
            Write a complete news article covering the {year} World Championship results.
            Include detailed tournament analysis and historical context.
            Format as a standalone news article with a title, date ({year}-11-15), and journalist byline."""
    }

    # Generate and save each article
    summary_path = os.path.join(year_dir, "yearly_summary.md")
    with open(summary_path, 'w', encoding='utf-8') as f:
        # Write year header
        f.write(f"# {year} Season Coverage\n\n")
        f.write("---\n\n")

        # Generate and append each article
        for section_name, prompt in section_prompts.items():
            try:
                context = f"\nHere's some context for the current season and previous year. Use it to create storylines for the upcoming season when relevant: {previous_summary}" if previous_summary else ""
                
                # Get relevant portions of results data for this section
                filtered_results = get_relevant_results(results_data, section_name)
                
                response = flash_model.generate_content(
                    prompt + context + f"\n\nResults data:\n{json.dumps(filtered_results)}",
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 10,
                        "max_output_tokens": 8192
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
                
                # Write article with separator
                f.write(f"{response.text}\n\n")
                f.write("---\n\n")
                
            except Exception as e:
                print(f"Error generating {section_name} article: {str(e)}")
                f.write(f"[Error generating {section_name} article]\n\n---\n\n")

    # Read and return the complete collection
    with open(summary_path, 'r', encoding='utf-8') as f:
        return f.read()

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
    
    # No longer automatically generate yearly summary after World Championship

def clear_previous_results():
    """Clear the previous_results directory if it exists"""
    base_dir = "previous_results"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)