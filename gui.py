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
        self.current_region = region  # Set the current region
        # Adjusted file name to match the actual file's case
        file_path = Path(f"previous_results/{self.current_year}/{region}_results.txt")
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
            if section != "Regular Season" and section in self.section_frames:
                self.section_frames[section].config(text=text)
        
        # Update standings text separately
        if "Regular Season" in sections:
            standings_text = ""
            for line in sections["Regular Season"].split('\n'):
                if "Standings:" in line or (line.strip() and line[0].isdigit()):
                    standings_text += line + '\n'
            self.standings_text.config(text=standings_text)

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
                section_content.append(line)
        
        # Add the last section
        if current_section:
            sections[current_section] = '\n'.join(section_content)
        
        return sections

    def show_match_viewer(self):
        if not self.match_viewer:
            # Create new window for match viewer
            viewer_window = tk.Toplevel(self)
            viewer_window.title("Regular Season Results")
            viewer_window.geometry("1200x800")
            
            self.match_viewer = MatchDetailsViewer(viewer_window)
            self.match_viewer.pack(fill=tk.BOTH, expand=True)
        
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
        print(f"Looking for matches for team: {team}")
        # Clear existing matches
        for widget in self.scrollable_matches_frame.winfo_children():
            widget.destroy()
            
        self.matches_title.config(text=f"{team} Matches")
        
        # Find and display all matches for the team
        matches = self.find_team_matches(team)
        print(f"Found {len(matches)} matches")
        
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

if __name__ == "__main__":
    app = ResultsViewer()
    app.mainloop()
