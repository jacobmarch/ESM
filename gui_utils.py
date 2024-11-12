# utils.py

from pathlib import Path

def get_available_years(results_dir="previous_results"):
    results_path = Path(results_dir)
    if not results_path.exists():
        return []
    return sorted([d.name for d in results_path.iterdir() if d.is_dir()])

def parse_results_file(content):
    sections = {
        "Off-Season": "",
        "Preseason": "",
        "Regular Season": "",
        "Playoffs": ""
    }
    
    current_section = None
    section_content = []
    
    for line in content.split('\n'):
        # Detect section headers
        if "Off-Season Results" in line:
            current_section = "Off-Season"
        elif "Preseason Preview" in line:
            if current_section:
                sections[current_section] = '\n'.join(section_content)
            current_section = "Preseason"
            section_content = []
        elif "Regular Season Results" in line:
            if current_section:
                sections[current_section] = '\n'.join(section_content)
            current_section = "Regular Season"
            section_content = []
        elif "Playoff Results" in line:
            if current_section:
                sections[current_section] = '\n'.join(section_content)
            current_section = "Playoffs"
            section_content = []
        elif current_section:
            # Skip empty lines at the start of sections
            if not section_content and not line.strip():
                continue
            # Add content line
            section_content.append(line)
    
    # Add the last section
    if current_section:
        sections[current_section] = '\n'.join(section_content)
    
    # Process each section to extract relevant information
    if "Regular Season" in sections:
        standings = []
        matches = []
        
        lines = sections["Regular Season"].split('\n')
        in_standings = False
        in_matches = False
        
        for line in lines:
            if "Regular Season Standings:" in line:
                in_standings = True
                in_matches = False
                continue
            elif "Match Results:" in line:
                in_standings = False
                in_matches = True
                continue
            
            if in_standings and line.strip() and not line.startswith('--'):
                standings.append(line.strip())
            elif in_matches and line.startswith('('):
                matches.append(line.strip())
        
        sections["Regular Season"] = {
            "standings": standings,
            "matches": matches
        }
    
    return sections

def extract_playoff_standings(playoff_text):
    standings = []
    lines = playoff_text.split('\n')
    for idx, line in enumerate(lines):
        if "Final Standings:" in line:
            while idx + 1 < len(lines) and lines[idx + 1].strip():
                standings.append(lines[idx + 1].strip())
                idx += 1
            break
    return "\n".join(["Final Standings:"] + standings)
