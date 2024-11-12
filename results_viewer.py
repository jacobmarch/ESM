# results_viewer.py

import tkinter as tk
from tkinter import ttk
from pathlib import Path
import os

from gui_utils import get_available_years, parse_results_file, extract_playoff_standings
from match_details_viewer import MatchDetailsViewer
from playoff_viewer import PlayoffViewer

REGIONS = ["Americas", "Europe", "Pacific", "China", "World Championship"]
SECTIONS = ["Off-Season", "Preseason", "Regular Season", "Playoffs"]

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
        years = get_available_years()
        
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
        
        for region in REGIONS:
            btn = ttk.Button(self.region_frame, text=region,
                           command=lambda r=region: self.select_region(r))
            btn.pack(side=tk.LEFT, padx=5)
        
        # Content frame with sections
        self.content_frame = ttk.Frame(self.dashboard_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the four sections
        self.section_frames = {}
        
        for i, section in enumerate(SECTIONS):
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
        file_path = Path(f"previous_results/{self.current_year}/{region}_results.txt")
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return
        
        # Read and parse the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract sections
        sections = parse_results_file(content)
        
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
                standings = extract_playoff_standings(text)
                self.playoff_standings.config(text=standings)
            elif section in self.section_frames:
                # For other sections that are still strings
                self.section_frames[section].config(text=text)
    
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
