import tkinter as tk
from tkinter import ttk
import os
from pathlib import Path
import markdown
from tkhtmlview import HTMLLabel

class ResultsViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Esports Manager Results Viewer")
        self.geometry("1920x1080")
        
        # Initialize tracking variables
        self.current_year = None
        self.current_region = None
        
        # Initialize views
        self.setup_year_view()
        self.setup_dashboard()
        
        # Initially show year view
        self.show_year_view()

    def setup_year_view(self):
        self.year_frame = ttk.Frame(self)
        
        # Get available years from directory
        years = self.get_available_years()
        
        # Create year buttons
        for year in years:
            btn = ttk.Button(self.year_frame, text=year,
                           command=lambda y=year: self.select_year(y))
            btn.pack(pady=5)

    def setup_dashboard(self):
        self.dashboard_frame = ttk.Frame(self)
        
        # Region buttons frame
        self.region_frame = ttk.Frame(self.dashboard_frame)
        self.region_frame.pack(fill=tk.X, pady=10)
        
        regions = ["Americas", "Europe", "Pacific", "China", "World Championship"]
        for region in regions:
            btn = ttk.Button(self.region_frame, text=region,
                           command=lambda r=region: self.select_region(r))
            btn.pack(side=tk.LEFT, padx=5)
        
        # Content frame with sections
        self.content_frame = ttk.Frame(self.dashboard_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the four sections
        sections = ["Off-Season", "Preseason", "Regular Season", "Playoffs"]
        self.section_frames = {}
        
        for i, section in enumerate(sections):
            # Create a label frame for the section
            section_frame = ttk.LabelFrame(self.content_frame, text=section)
            section_frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")
            
            # Add a canvas and scrollbar for scrolling
            canvas = tk.Canvas(section_frame)
            scrollbar = ttk.Scrollbar(section_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            # Configure the canvas
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack the scrollbar and canvas
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Create a window in the canvas for the scrollable frame
            canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            
            # Configure the scrollable frame to expand to canvas width
            def configure_scroll_region(event, canvas=canvas):
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            def configure_frame_width(event, canvas=canvas, canvas_frame=canvas_frame):
                canvas.itemconfig(canvas_frame, width=event.width)
            
            scrollable_frame.bind("<Configure>", configure_scroll_region)
            canvas.bind("<Configure>", configure_frame_width)
            
            if section == "Regular Season":
                # Special handling for Regular Season section
                self.standings_text = ttk.Label(scrollable_frame, wraplength=500)
                self.standings_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                
                # Add view results button
                self.match_viewer = None
                ttk.Button(scrollable_frame, text="View Results", 
                    command=self.show_match_viewer).pack(pady=5)
            elif section == "Playoffs":
                # Special handling for Playoffs section
                self.playoff_standings = ttk.Label(scrollable_frame, wraplength=500)
                self.playoff_standings.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                
                # Add view playoff bracket button
                self.playoff_viewer = None
                ttk.Button(scrollable_frame, text="View Playoff Bracket", 
                          command=self.show_playoff_viewer).pack(pady=5)
            else:
                # Other sections get regular labels
                self.section_frames[section] = ttk.Label(scrollable_frame, wraplength=500)
                self.section_frames[section].pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
        # Configure grid weights
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

    def get_available_years(self):
        results_path = Path("previous_results")
        if not results_path.exists():
            return []
        return sorted([d.name for d in results_path.iterdir() if d.is_dir()])

    def show_year_view(self):
        self.dashboard_frame.pack_forget()
        self.year_frame.pack(fill=tk.BOTH, expand=True)

    def show_dashboard(self):
        self.year_frame.pack_forget()
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)

    def select_year(self, year):
        self.current_year = year
        self.show_dashboard()

    def select_region(self, region):
        self.current_region = region
        file_path = Path(f"previous_results/{self.current_year}/{self.current_region}_results.txt")
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return
        
        # Read and parse the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract sections
        sections = self.parse_results_file(content)
        
        # Update section contents
        for section, text in sections.items():
            if section == "Regular Season":
                # Regular Season is now a dict with standings and matches
                if isinstance(text, dict):  # Check if text is a dictionary
                    standings_text = "Regular Season Standings:\n"
                    standings_text += "\n".join(text["standings"])
                    self.standings_text.config(text=standings_text)
                else:  # Handle legacy format where text might be a string
                    self.standings_text.config(text=text)
            elif section == "Playoffs":
                # Extract final standings from playoff section
                standings = self.extract_playoff_standings(text)
                self.playoff_standings.config(text=standings)
            elif section in self.section_frames:
                # For other sections that are still strings
                self.section_frames[section].config(text=text)

    def parse_results_file(self, content):
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

    def extract_playoff_standings(self, playoff_text):
        standings = []
        lines = playoff_text.split('\n')
        for line in lines:
            if "Final Standings:" in line:
                idx = lines.index(line)
                while idx + 1 < len(lines) and lines[idx + 1].strip():
                    standings.append(lines[idx + 1])
                    idx += 1
                break
        return "\n".join(["Final Standings:"] + standings)

    def show_match_viewer(self):
        if self.match_viewer:
            # If match viewer exists but window was closed
            if not self.match_viewer.winfo_exists():
                self.match_viewer = None
        
        if not self.match_viewer:
            # Create new window for match viewer
            viewer_window = tk.Toplevel(self)
            viewer_window.title("Regular Season Results")
            viewer_window.geometry("1200x800")
            
            # Create new match viewer
            self.match_viewer = MatchDetailsViewer(viewer_window)
            self.match_viewer.pack(fill=tk.BOTH, expand=True)
            
            # Handle window closing
            def on_closing():
                self.match_viewer = None
                viewer_window.destroy()
                
            viewer_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Extract standings from current content
        standings = []
        current_text = self.standings_text.cget("text")
        for line in current_text.split('\n'):
            if line.strip() and not line.startswith('Regular Season'):
                standings.append(line.strip())
        
        # Get the current region's content
        file_path = Path(f"previous_results/{self.current_year}/{self.current_region}_results.txt")
        print(f"Loading results from: {file_path}")
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"Content length: {len(content)}")
                self.match_viewer.current_content = content
        
        self.match_viewer.load_teams(standings)

    def show_playoff_viewer(self):
        print("Opening playoff viewer")  # Debug print
        
        if self.playoff_viewer:
            if not self.playoff_viewer.winfo_exists():
                self.playoff_viewer = None
        
        if not self.playoff_viewer:
            viewer_window = tk.Toplevel(self)
            viewer_window.title(f"{self.current_region} Playoffs")
            viewer_window.geometry("1200x800")
            
            self.playoff_viewer = PlayoffViewer(viewer_window)
            self.playoff_viewer.pack(fill=tk.BOTH, expand=True)
            
            # Load playoff data
            file_path = Path(f"previous_results/{self.current_year}/{self.current_region}_results.txt")
            print(f"Loading file: {file_path}")  # Debug print
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    playoff_data = self.extract_playoff_matches(content)
                    if playoff_data:
                        print(f"Loading {len(playoff_data)} matches into viewer")  # Debug print
                        self.playoff_viewer.load_playoff_data(playoff_data)
                    else:
                        print("No playoff data found")
            else:
                print("File not found:", file_path)  # Debug print
            
            def on_closing():
                self.playoff_viewer = None
                viewer_window.destroy()
            
            viewer_window.protocol("WM_DELETE_WINDOW", on_closing)

    def extract_playoff_matches(self, content):
        print("Extracting playoff matches from content")
        matches = []
        
        # Find the playoff section based on region
        playoff_header = f"{self.current_region} Playoff Results"
        if playoff_header not in content:
            print(f"No playoff section found for header: {playoff_header}")
            return matches
            
        playoff_section = content.split(playoff_header)[1].split("Final Standings:")[0]
        
        current_round = None
        current_bracket = None
        round_number = 0
        
        for line in playoff_section.split('\n'):
            line = line.strip()
            
            if not line:
                continue
                
            if line.startswith("Round"):
                round_number += 1
                continue
                
            if "Upper Bracket:" in line:
                current_bracket = "upper"
                current_round = f"upper{round_number}"
                continue
                
            if "Lower Bracket:" in line:
                current_bracket = "lower"
                current_round = f"lower{round_number}"
                continue
                
            if "Lower Bracket with Upper Losers:" in line:
                current_bracket = "lower"
                current_round = f"lower{round_number}"
                continue
                
            if "Grand Final:" in line:
                current_round = "grand_finals"
                continue
                
            if "(" in line and ")" in line and "-" in line and "Map Sequence:" not in line:
                try:
                    # Parse match line
                    parts = line.split(" - ")
                    if len(parts) == 2:
                        # Extract team1 details
                        team1_part = parts[0].split()
                        rating1 = team1_part[0].strip("()")
                        score1 = team1_part[-1]
                        team1 = " ".join(team1_part[1:-1])
                        
                        # Extract team2 details
                        team2_part = parts[1].split()
                        score2 = team2_part[0]
                        team2_with_rating = " ".join(team2_part[1:])
                        team2 = team2_with_rating.split(" (")[0]
                        rating2 = team2_with_rating.split(" (")[1].strip(")")
                        
                        match = {
                            'round': current_round,
                            'team1': team1,
                            'team2': team2,
                            'score1': score1,
                            'score2': score2,
                            'rating1': rating1,
                            'rating2': rating2
                        }
                        matches.append(match)
                        print(f"Added match: {match}")
                except Exception as e:
                    print(f"Error parsing match line: {line}")
                    print(f"Error details: {str(e)}")
        
        print(f"Total matches extracted: {len(matches)}")
        return matches

class MatchDetailsViewer(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Split window into two panes
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left pane - Teams
        self.teams_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.teams_frame, weight=1)
        
        # Teams scrollable area
        self.teams_canvas = tk.Canvas(self.teams_frame, width=200)
        self.teams_scrollbar = ttk.Scrollbar(self.teams_frame, orient="vertical", command=self.teams_canvas.yview)
        self.scrollable_teams_frame = ttk.Frame(self.teams_canvas)
        
        self.teams_canvas.configure(yscrollcommand=self.teams_scrollbar.set)
        
        # Pack teams scrollbar and canvas
        self.teams_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.teams_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create teams window
        self.teams_window = self.teams_canvas.create_window((0, 0), window=self.scrollable_teams_frame, anchor="nw")
        
        # Right pane - Matches
        self.matches_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.matches_frame, weight=3)
        
        # Matches title
        self.matches_title = ttk.Label(self.matches_frame, text="Select a team to view matches", font=("Arial", 12, "bold"))
        self.matches_title.pack(pady=10)
        
        # Matches scrollable area
        self.matches_canvas = tk.Canvas(self.matches_frame)
        self.matches_scrollbar = ttk.Scrollbar(self.matches_frame, orient="vertical", command=self.matches_canvas.yview)
        self.scrollable_matches_frame = ttk.Frame(self.matches_canvas)
        
        self.matches_canvas.configure(yscrollcommand=self.matches_scrollbar.set)
        
        # Pack matches scrollbar and canvas
        self.matches_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.matches_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create matches window
        self.matches_window = self.matches_canvas.create_window((0, 0), window=self.scrollable_matches_frame, anchor="nw")
        
        # Configure scrolling
        def configure_teams_scroll(event):
            self.teams_canvas.configure(scrollregion=self.teams_canvas.bbox("all"))
            self.teams_canvas.itemconfig(self.teams_window, width=self.teams_canvas.winfo_width())
            
        def configure_matches_scroll(event):
            self.matches_canvas.configure(scrollregion=self.matches_canvas.bbox("all"))
            self.matches_canvas.itemconfig(self.matches_window, width=self.matches_canvas.winfo_width())
        
        self.scrollable_teams_frame.bind("<Configure>", configure_teams_scroll)
        self.scrollable_matches_frame.bind("<Configure>", configure_matches_scroll)
        
        # Store the current results file content
        self.current_content = ""

    def load_teams(self, standings):
        # Clear existing teams
        for widget in self.scrollable_teams_frame.winfo_children():
            widget.destroy()
            
        # Create team buttons
        for team_data in standings:
            # Skip empty lines
            if not team_data.strip():
                continue
                
            # Extract team name by finding the first digit and taking everything after it
            # until the record (which is in parentheses or has numbers with dashes)
            parts = team_data.split()
            if not parts or not any(c.isdigit() for c in parts[0]):
                continue
                
            # Find where the team name starts (after the ranking number)
            start_idx = team_data.find('. ') + 2 if '. ' in team_data else 0
            
            # Find where the record starts (it will be in the format X-X)
            end_idx = team_data.rfind(' ')
            while end_idx > 0 and not team_data[end_idx:].strip()[0].isdigit():
                end_idx = team_data.rfind(' ', 0, end_idx)
                
            if start_idx >= end_idx:
                continue
                
            team_name = team_data[start_idx:end_idx].strip()
            
            btn = ttk.Button(self.scrollable_teams_frame, text=team_name,
                            command=lambda t=team_name: self.show_team_matches(t))
            btn.pack(pady=2)

    def show_team_matches(self, team):
        # Clear existing matches
        for widget in self.scrollable_matches_frame.winfo_children():
            widget.destroy()
            
        self.matches_title.config(text=f"{team} Matches")
        
        # Find and display all matches for the team
        matches = self.find_team_matches(team)
        
        if not matches:
            # Show "No matches found" message
            ttk.Label(self.scrollable_matches_frame, 
                     text="No matches found for this team",
                     font=("Arial", 10)).pack(pady=20)
        else:
            # Create widgets for each match
            for match in matches:
                print(f"Creating widget for match: {match}")
                self.create_match_widget(match)

    def find_team_matches(self, team):
        print(f"Searching for matches with team: {team}")
        matches = []
        lines = self.current_content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for lines that start with a rating in parentheses
            if line.startswith('(') and team in line:
                try:
                    # Extract the teams and scores
                    match_line = line[line.find(')') + 1:].strip()
                    teams_and_scores = match_line.split(' - ')
                    
                    # Split first part into team1 and score1
                    team1_parts = teams_and_scores[0].rsplit(' ', 1)
                    team1 = team1_parts[0].strip()
                    score1 = team1_parts[1]
                    
                    # Split second part into score2 and team2
                    team2_parts = teams_and_scores[1].split(' ', 1)
                    score2 = team2_parts[0]
                    team2 = team2_parts[1].split('(')[0].strip()  # Remove rating at end
                    
                    match_data = {
                        'team1': team1,
                        'team2': team2,
                        'score1': score1,
                        'score2': score2,
                        'maps': []
                    }
                    
                    # Look for map details
                    i += 1
                    while i < len(lines) and lines[i].strip():
                        if "Map Sequence:" in lines[i]:
                            i += 1
                            # Skip ban/pick/decider lines
                            while i < len(lines) and ("ban:" in lines[i] or "pick:" in lines[i] or "Decider:" in lines[i]):
                                i += 1
                            # Get map results
                            while i < len(lines) and ":" in lines[i] and not lines[i].startswith('('):
                                map_line = lines[i].strip()
                                map_name, score = map_line.split(':')
                                if not any(x in map_line.lower() for x in ['ban:', 'pick:', 'decider:']):
                                    match_data['maps'].append({
                                        'name': map_name.strip(),
                                        'score': score.strip()
                                    })
                                i += 1
                            i -= 1  # Back up one line
                            break
                    
                    matches.append(match_data)
                    print(f"Found match: {team1} vs {team2}")
                    
                except Exception as e:
                    print(f"Error parsing match line: {line}")
                    print(f"Error details: {str(e)}")
            i += 1
        
        print(f"Total matches found for {team}: {len(matches)}")
        return matches

    def create_match_widget(self, match_data):
        # Create a frame for this match
        match_frame = ttk.Frame(self.scrollable_matches_frame)
        match_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Match score
        score_text = f"{match_data['team1']} {match_data['score1']} - {match_data['score2']} {match_data['team2']}"
        score_label = ttk.Label(match_frame, text=score_text, font=("Arial", 10))
        score_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Details button and frame
        details_frame = ttk.Frame(self.scrollable_matches_frame)
        
        def toggle_details():
            if details_frame.winfo_manager():
                details_frame.pack_forget()
            else:
                details_frame.pack(fill=tk.X, padx=30, pady=(0, 10))
                # Show map details
                for map_info in match_data['maps']:
                    ttk.Label(details_frame, 
                            text=f"{map_info['name']}: {map_info['score']}",
                            font=("Arial", 9)).pack(anchor='w')
        
        ttk.Button(match_frame, text="Details", command=toggle_details).pack(side=tk.RIGHT)

class PlayoffViewer(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        # Create main layout
        self.bracket_canvas = tk.Canvas(self, bg='white')
        self.bracket_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Initialize matches list
        self.matches = []
        
        # Add scrollbars
        self.v_scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.bracket_canvas.yview)
        self.h_scrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.bracket_canvas.xview)
        self.bracket_canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Pack scrollbars
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind resize event
        self.bracket_canvas.bind('<Configure>', lambda e: self.draw_bracket())

    def load_playoff_data(self, matches):
        print("Loading playoff data:", matches)  # Debug print
        self.matches = matches
        self.draw_bracket()

    def draw_bracket(self):
        # Clear canvas
        self.bracket_canvas.delete("all")
        
        # Safety check - if no matches, draw empty bracket
        if not self.matches:
            self.bracket_canvas.create_text(
                self.bracket_canvas.winfo_width() / 2,
                self.bracket_canvas.winfo_height() / 2,
                text="No matches to display",
                font=("Arial", 14)
            )
            return
        
        # Get canvas dimensions
        canvas_width = self.bracket_canvas.winfo_width()
        canvas_height = self.bracket_canvas.winfo_height()
        
        # Constants for layout
        box_width = 200
        box_height = 60
        h_gap = 150  # Horizontal gap between rounds
        v_gap = 100  # Vertical gap between matches
        
        # Starting positions
        start_x = 50
        upper_y = 50
        
        # Draw Upper Bracket
        x = start_x
        y = upper_y
        
        # Safely filter matches
        def safe_round_check(match, prefix):
            round_value = match.get('round')
            return round_value is not None and str(round_value).startswith(prefix)
        
        upper_matches = [m for m in self.matches if safe_round_check(m, 'upper')]
        
        # Draw each round
        round_positions = {}  # Store positions for connecting lines
        
        # Upper Bracket
        rounds = ['upper1', 'upper2', 'upper3']
        for round_idx, round_name in enumerate(rounds):
            round_matches = [m for m in self.matches if m.get('round') == round_name]
            y = upper_y
            round_positions[round_name] = []
            
            for match in round_matches:
                # Draw match box
                box_coords = (x, y, x + box_width, y + box_height)
                self.bracket_canvas.create_rectangle(box_coords, fill='white', outline='black')
                match['bbox'] = box_coords
                round_positions[round_name].append((x, y))
                
                # Draw match text
                text = f"{match.get('team1', 'TBD')}\n{match.get('score1', '0')} - {match.get('score2', '0')}\n{match.get('team2', 'TBD')}"
                self.bracket_canvas.create_text(x + box_width/2, y + box_height/2,
                                             text=text, width=box_width-10,
                                             anchor='center', justify='center')
                
                y += v_gap * (2 ** round_idx)
            
            x += box_width + h_gap
        
        # Lower Bracket
        lower_y = upper_y + v_gap * 3
        x = start_x + (box_width + h_gap) / 2
        rounds = ['lower1', 'lower2', 'lower3', 'lower4']
        
        for round_idx, round_name in enumerate(rounds):
            round_matches = [m for m in self.matches if m.get('round') == round_name]
            y = lower_y
            round_positions[round_name] = []
            
            for match in round_matches:
                # Draw match box
                box_coords = (x, y, x + box_width, y + box_height)
                self.bracket_canvas.create_rectangle(box_coords, fill='white', outline='black')
                match['bbox'] = box_coords
                round_positions[round_name].append((x, y))
                
                # Draw match text
                text = f"{match.get('team1', 'TBD')}\n{match.get('score1', '0')} - {match.get('score2', '0')}\n{match.get('team2', 'TBD')}"
                self.bracket_canvas.create_text(x + box_width/2, y + box_height/2,
                                             text=text, width=box_width-10,
                                             anchor='center', justify='center')
                
                y += v_gap
            
            x += box_width + h_gap
        
        # Grand Finals
        finals = [m for m in self.matches if m.get('round') == 'grand_finals']
        if finals:
            match = finals[0]
            final_x = x
            final_y = canvas_height * 0.4
            
            # Draw finals box
            box_coords = (final_x, final_y, final_x + box_width, final_y + box_height)
            self.bracket_canvas.create_rectangle(box_coords, fill='white', outline='black')
            match['bbox'] = box_coords
            
            # Draw finals text
            text = f"Grand Finals\n{match.get('team1', 'TBD')}\n{match.get('score1', '0')} - {match.get('score2', '0')}\n{match.get('team2', 'TBD')}"
            self.bracket_canvas.create_text(final_x + box_width/2, final_y + box_height/2,
                                         text=text, width=box_width-10,
                                         anchor='center', justify='center')
        
        # Draw connecting lines
        for round_name, positions in round_positions.items():
            if len(positions) >= 2:
                for i in range(0, len(positions), 2):
                    if i + 1 < len(positions):
                        x1, y1 = positions[i][0] + box_width, positions[i][1] + box_height/2
                        x2, y2 = positions[i+1][0] + box_width, positions[i+1][1] + box_height/2
                        mid_x = x1 + (h_gap/2)
                        
                        # Draw lines to next round
                        self.bracket_canvas.create_line(x1, y1, mid_x, y1, fill='black')
                        self.bracket_canvas.create_line(x1, y2, mid_x, y2, fill='black')
                        self.bracket_canvas.create_line(mid_x, y1, mid_x, y2, fill='black')
                        self.bracket_canvas.create_line(mid_x, (y1+y2)/2, mid_x + h_gap/2, (y1+y2)/2, fill='black')

    def on_canvas_click(self, event):
        # Check if click is within any match box
        for match in self.matches:
            if 'bbox' in match:
                x1, y1, x2, y2 = match['bbox']
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    self.show_match_details(match)
                    break

    def show_match_details(self, match):
        # Clear existing details
        for widget in self.details_content.winfo_children():
            widget.destroy()
        
        # Show match details
        title = f"{match['team1']} vs {match['team2']}"
        self.details_title.config(text=title)
        
        score = f"Final Score: {match['score1']} - {match['score2']}"
        ttk.Label(self.details_content, text=score, font=("Arial", 10, "bold")).pack(pady=10)
        
        # Show map details
        ttk.Label(self.details_content, text="Maps:", font=("Arial", 10, "bold")).pack(pady=(10,5))
        for map_info in match['maps']:
            ttk.Label(self.details_content, 
                     text=f"{map_info['name']}: {map_info['score']}",
                     font=("Arial", 9)).pack(anchor='w')

if __name__ == "__main__":
    app = ResultsViewer()
    app.mainloop()
