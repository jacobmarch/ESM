# Adding a PyQt UI to Your Game Simulation

To enhance your game simulation by transitioning from a console-based output to a more user-friendly graphical interface using PyQt, follow the comprehensive plan below. This plan ensures that your existing simulation logic remains untouched while improving how results are displayed and navigated by the user.

## **1. Project Structure**

Organize your project to separate UI components from the simulation logic. This separation promotes maintainability and scalability.

```
game/
│
├── data/
│   ├── first_names.txt
│   ├── last_names.txt
│   ├── gamer_tags.txt
│   └── team_names.txt
│
├── ui/
│   ├── main_window.py
│   ├── league_view.py
│   ├── match_view.py
│   ├── world_championship_view.py
│   └── resources.qrc
│
├── __init__.py
├── team.py
├── player.py
├── match.py
├── league.py
├── tournament.py
├── season.py
├── manager.py
├── world_championship.py
└── utils.py
```

## **2. Set Up the PyQt Environment**

Ensure you have PyQt5 installed. You can install it using pip:

```bash
pip install PyQt5
```

## **3. Design the UI Components**

### **a. Main Window**

The main window serves as the central hub, containing tabs or sections for different parts of the simulation (e.g., Leagues, Teams, Matches, World Championship).

```python
# ui/main_window.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from .league_view import LeagueView
from .world_championship_view import WorldChampionshipView

class MainWindow(QMainWindow):
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        self.setWindowTitle("Game Simulation")
        self.setGeometry(100, 100, 1024, 768)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Initialize different views
        self.league_view = LeagueView(self.game_manager)
        self.tabs.addTab(self.league_view, "Leagues")
        
        self.world_championship_view = WorldChampionshipView(self.game_manager)
        self.tabs.addTab(self.world_championship_view, "World Championship")
        
        # Add more tabs as needed

if __name__ == "__main__":
    app = QApplication(sys.argv)
    from manager import GameManager
    game_manager = GameManager()
    window = MainWindow(game_manager)
    window.show()
    sys.exit(app.exec_())
```

### **b. League View**

Displays information related to leagues, teams, and their statuses. It allows users to select a league and view its details.

```python
# ui/league_view.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QComboBox, QTableWidget, QTableWidgetItem

class LeagueView(QWidget):
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Dropdown to select a league
        self.league_selector = QComboBox()
        self.league_selector.addItems([league.name for league in self.game_manager.leagues])
        layout.addWidget(self.league_selector)
        
        # Button to view league details
        self.view_button = QPushButton("View League")
        self.view_button.clicked.connect(self.view_league)
        layout.addWidget(self.view_button)
        
        # Table to display league details
        self.league_table = QTableWidget()
        self.league_table.setColumnCount(3)
        self.league_table.setHorizontalHeaderLabels(["Team Name", "Region", "Average Skill"])
        layout.addWidget(self.league_table)
        
        self.setLayout(layout)
    
    def view_league(self):
        selected_league_name = self.league_selector.currentText()
        selected_league = next((league for league in self.game_manager.leagues if league.name == selected_league_name), None)
        
        if selected_league:
            teams = selected_league.teams
            self.league_table.setRowCount(len(teams))
            for row, team in enumerate(teams):
                self.league_table.setItem(row, 0, QTableWidgetItem(team.name))
                self.league_table.setItem(row, 1, QTableWidgetItem(team.region))
                self.league_table.setItem(row, 2, QTableWidgetItem(f"{team.get_average_skill():.2f}"))
```

### **c. World Championship View**

Handles the display and management of the World Championship results.

```python
# ui/world_championship_view.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit

class WorldChampionshipView(QWidget):
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Button to run the World Championship simulation
        self.run_button = QPushButton("Run World Championship")
        self.run_button.clicked.connect(self.run_championship)
        layout.addWidget(self.run_button)
        
        # Text area to display results
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        layout.addWidget(self.results_display)
        
        self.setLayout(layout)
    
    def run_championship(self):
        championship = self.game_manager.run_world_championship()
        results = "World Championship Results:\n"
        for match in championship.match_results:
            results += f"{match}\n"
        self.results_display.setText(results)
```

### **d. Additional Views**

Depending on your requirements, you can create additional views such as `MatchView`, `TeamView`, etc., following a similar pattern.

## **4. Integrate the UI with the Simulation Logic**

### **a. Modify the Game Manager**

Update the `GameManager` to initialize and interact with the UI instead of using console-based interactions.

```python
# manager.py
import sys
from ui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication

class GameManager:
    def __init__(self):
        self.leagues = [
            League("Americas"),
            League("Europe"),
            League("China"),
            League("Pacific")
        ]
        self.current_year = 2023
        self.current_phase = "Off-Season"
        self.phases = ["Off-Season", "Preseason", "Regular Season", "Playoffs", "World Championship"]
        # Initialize other attributes as needed
    
    def start_game(self):
        app = QApplication(sys.argv)
        self.ui = MainWindow(self)
        self.ui.show()
        sys.exit(app.exec_())
    
    def run_world_championship(self):
        world_championship = WorldChampionship(self.leagues)
        world_championship.run()
        return world_championship

    # Other existing methods remain unchanged

if __name__ == "__main__":
    manager = GameManager()
    manager.start_game()
```

### **b. Ensure Thread Safety**

If your simulation runs long processes, consider running them in separate threads to keep the UI responsive. PyQt provides `QThread` for this purpose.

```python
# Example: Running simulation in a separate thread
from PyQt5.QtCore import QThread, pyqtSignal

class SimulationThread(QThread):
    result_ready = pyqtSignal(str)
    
    def __init__(self, simulation_method, *args, **kwargs):
        super().__init__()
        self.simulation_method = simulation_method
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        result = self.simulation_method(*self.args, **self.kwargs)
        self.result_ready.emit(result)
```

Integrate `SimulationThread` within your UI components to handle long-running simulations without freezing the UI.

## **5. Update Output Handling**

### **a. Redirect Simulation Outputs to UI**

Modify methods in your simulation classes (`Match`, `League`, etc.) to return results rather than printing them. This allows the UI to capture and display the results.

```python
# Example modification in Match class
class Match:
    # Existing methods...
    
    def play(self):
        home_wins = 0
        away_wins = 0
        games_to_win = (self.best_of // 2) + 1
        games_played = []

        while home_wins < games_to_win and away_wins < games_to_win:
            home_score, away_score, round_details = self.simulate_game()
            games_played.append((home_score, away_score, round_details))

            if home_score > away_score:
                home_wins += 1
            else:
                away_wins += 1

        winner = self.home_team if home_wins > away_wins else self.away_team
        loser = self.away_team if home_wins > away_wins else self.home_team

        result = {
            'home_team': self.home_team,
            'away_team': self.away_team,
            'home_score': home_wins,
            'away_score': away_wins,
            'winner': winner,
            'loser': loser,
            'games': games_played
        }
        return result
```

### **b. Display Results in UI**

Use the returned results from simulation methods to update UI components instead of printing to the console.

```python
# Example in WorldChampionshipView
def run_championship(self):
    self.run_button.setEnabled(False)
    self.results_display.setText("Running World Championship...\n")
    
    def handle_results(result):
        results = "World Championship Results:\n"
        for match in result.match_results:
            results += f"{match}\n"
        self.results_display.setText(results)
        self.run_button.setEnabled(True)
    
    # Run the simulation in a separate thread if it's time-consuming
    self.thread = SimulationThread(self.game_manager.run_world_championship)
    self.thread.result_ready.connect(handle_results)
    self.thread.start()
```

## **6. Enhance User Navigation and Experience**

### **a. Use Layouts Effectively**

Ensure your UI layout is intuitive. Utilize `QVBoxLayout`, `QHBoxLayout`, and `QGridLayout` to organize widgets logically.

### **b. Implement Search and Filter Features**

Allow users to search for specific teams, players, or matches within the UI.

```python
# Example: Adding a search bar in LeagueView
from PyQt5.QtWidgets import QLineEdit

class LeagueView(QWidget):
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Existing widgets...

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search team...")
        self.search_bar.textChanged.connect(self.filter_teams)
        layout.addWidget(self.search_bar)
        
        # Existing widgets...
    
    def filter_teams(self, text):
        for row in range(self.league_table.rowCount()):
            item = self.league_table.item(row, 0)  # Team Name column
            if text.lower() in item.text().lower():
                self.league_table.setRowHidden(row, False)
            else:
                self.league_table.setRowHidden(row, True)
```

### **c. Incorporate Visual Elements**

Enhance readability and aesthetics by adding charts, graphs, or progress bars using libraries like `matplotlib` integrated with PyQt.

```python
# Example: Displaying a skill distribution chart
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class LeagueView(QWidget):
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Existing widgets...

        # Matplotlib Figure
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
    
    def view_league(self):
        # Existing code to populate table
        
        # Plotting skill distribution
        skills = [team.get_average_skill() for team in selected_league.teams]
        self.ax.clear()
        self.ax.hist(skills, bins=10, color='skyblue', edgecolor='black')
        self.ax.set_title("Skill Distribution")
        self.ax.set_xlabel("Average Skill")
        self.ax.set_ylabel("Number of Teams")
        self.canvas.draw()
```

## **7. Testing and Validation**

- **Unit Testing:** Write tests for UI components to ensure they display data correctly.
- **Integration Testing:** Verify that the UI correctly interacts with the simulation logic.
- **User Testing:** Gather feedback from users to improve usability and functionality.

## **8. Additional Enhancements**

- **Export Functionality:** Allow users to export simulation results to formats like CSV or PDF.
- **Real-Time Updates:** If simulations can run in real-time, update the UI dynamically to reflect ongoing changes.
- **User Settings:** Provide options for users to customize views, such as theme selection or data display preferences.

## **Summary**

By following this plan, you can seamlessly integrate a PyQt-based UI into your existing game simulation project. This integration will enhance user interaction, make navigation more intuitive, and present simulation results in a visually appealing and organized manner without altering the core simulation logic.