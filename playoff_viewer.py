# playoff_viewer.py

import tkinter as tk
from tkinter import ttk

class PlayoffViewer(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)

        # Create main layout with left and right frames
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self, width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas for bracket
        self.bracket_canvas = tk.Canvas(self.left_frame, bg='white')
        self.bracket_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Initialize matches list
        self.matches = []

        # Add scrollbars
        self.v_scrollbar = tk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.bracket_canvas.yview)
        self.h_scrollbar = tk.Scrollbar(self.left_frame, orient=tk.HORIZONTAL, command=self.bracket_canvas.xview)
        self.bracket_canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Pack scrollbars
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind resize and click events
        self.bracket_canvas.bind('<Configure>', lambda e: self.draw_bracket())
        self.bracket_canvas.bind('<Button-1>', self.on_canvas_click)

        # Details section in right frame
        self.details_title = ttk.Label(self.right_frame, text="Match Details", font=("Arial", 16, "bold"))
        self.details_title.pack(pady=10)

        self.details_content = ttk.Frame(self.right_frame)
        self.details_content.pack(fill=tk.BOTH, expand=True, padx=10)

    def load_playoff_data(self, matches):
        print("Loading playoff data:", matches)  # Debug print
        self.matches = matches
        self.draw_bracket()

    def draw_bracket(self):
        # Clear canvas
        self.bracket_canvas.delete("all")

        # Constants for layout
        box_width = 200
        box_height = 60
        h_gap = 150  # Horizontal gap between rounds
        v_gap = 100  # Vertical gap between matches

        # Starting positions
        start_x = 50
        upper_y = 50

        # Round definitions
        upper_rounds = ['upper1', 'upper2', 'upper3', 'upper_finals']
        lower_rounds = ['lower1', 'lower2', 'lower3', 'lower4', 'lower_finals']

        round_positions = {}

        # Draw Upper Bracket
        x = start_x
        for round_idx, round_name in enumerate(upper_rounds):
            round_matches = [m for m in self.matches if m.get('round') == round_name]
            y = upper_y + (v_gap * (2 ** round_idx - 1))
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

        # Draw Lower Bracket
        x = start_x + (box_width + h_gap) / 2
        lower_y = upper_y + v_gap * 2

        for round_idx, round_name in enumerate(lower_rounds):
            round_matches = [m for m in self.matches if m.get('round') == round_name]
            y = lower_y + (v_gap * (round_idx % 2))
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

                y += v_gap * 2

            x += box_width + h_gap

        # Grand Finals
        finals = [m for m in self.matches if m.get('round') == 'grand_finals']
        if finals:
            match = finals[0]
            final_x = x
            final_y = (upper_y + lower_y) / 2

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
        title = f"{match.get('team1', 'TBD')} vs {match.get('team2', 'TBD')}"
        ttk.Label(self.details_content, text=title, font=("Arial", 14, "bold")).pack(pady=10)

        score = f"Final Score: {match.get('score1', '0')} - {match.get('score2', '0')}"
        ttk.Label(self.details_content, text=score, font=("Arial", 12)).pack(pady=5)

        # Show team ratings
        ratings = f"Ratings: {match.get('rating1', '0')} - {match.get('rating2', '0')}"
        ttk.Label(self.details_content, text=ratings, font=("Arial", 12)).pack(pady=5)

        # Show map details if available
        maps = match.get('maps', [])
        if maps:
            ttk.Label(self.details_content, text="Maps:", font=("Arial", 12, "bold")).pack(pady=(10,5))
            for map_info in maps:
                map_text = f"{map_info.get('name', 'Unknown')}: {map_info.get('score', '0')}"
                ttk.Label(self.details_content, text=map_text, font=("Arial", 11)).pack(anchor='w')
