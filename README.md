# Esports Manager Game

## Project Overview
This is an Esports Manager Game simulation that models a professional esports ecosystem with multiple regional leagues competing through seasons, playoffs, and ultimately a World Championship. The game simulates player development, team management, and competitive matches in a Valorant-style format.

## Detailed Component Breakdown

### Core Game Flow (main.py)
Entry point that initializes and manages the game lifecycle:
- Clears any previous simulation results
- Creates a new GameManager instance
- Simulates initial off-season to set up the first year
- Starts the main game loop for continuous simulation

### Game Management (game/manager.py)
Central controller for the game's yearly cycle:
- Manages 4 regional leagues: Americas, Europe, China, and Pacific
- Progresses through 5 distinct phases:
  1. Off-Season: Player transfers and contract management
  2. Preseason: Team ratings and predictions
  3. Regular Season: League matches
  4. Playoffs: Regional championships
  5. World Championship: Global tournament
- Handles user interface and menu navigation
- Coordinates between leagues for World Championship qualification

### League System (game/league.py)
Manages individual regional competitions:
- Maintains roster of 10 teams per region
- Tracks team performance and standings
- Key functionalities:
  - Off-season roster management
  - Preseason power rankings and player highlights
  - Regular season match scheduling and results
  - Playoff tournament organization
  - Historical rating tracking for year-over-year comparison
- Generates detailed reports for each phase

### Season Management (game/season.py)
Handles regular season competition structure:
- Implements round-robin match scheduling
- Maintains league standings and points
- Features:
  - Match result processing
  - Standing calculations
  - Playoff qualification determination
  - Detailed match history tracking
- Provides formatted results for record-keeping

### World Championship (game/world_championship.py)
Implements the global championship tournament:
- Group Stage:
  - Creates 4 balanced groups with regional distribution
  - Double-elimination format within groups
  - Top 2 teams from each group advance
- Knockout Stage:
  - Seeded bracket based on group performance
  - Double-elimination format
  - Best-of-5 finals
- Comprehensive results tracking and formatting

### Tournament System (game/tournament.py)
Implements double-elimination tournament logic:
- Manages both upper and lower brackets
- Handles:
  - Match scheduling
  - Bracket progression
  - Loser bracket integration
  - Final standings calculation
- Supports different match formats (Best-of-3/Best-of-5)
- Provides detailed round-by-round results

### Match System (game/match.py)
Simulates individual matches between teams:
- Implements Valorant-style match format:
  - First to 13 rounds
  - Overtime rules for 12-12 ties
- Round simulation:
  - 5v5 player encounters
  - Skill-based outcome determination
  - Detailed encounter tracking
- Caches results for consistency
- Provides comprehensive match statistics

### Team Management (game/team.py)
Represents and manages individual teams:
- Maintains 5-player rosters
- Features:
  - Team skill calculation
  - Rating tracking between seasons
  - Roster management
  - Contract handling
- Performance comparison tools
- Rating change tracking

### Player System (game/player.py)
Models individual players:
- Attributes:
  - Real name (First and Last)
  - Gamer tag
  - Skill rating (50-100 scale)
  - Contract details
- Features:
  - Skill generation using normal distribution
  - Contract management
  - Performance improvement system
  - String representation for display

### Utility Functions (game/utils.py)
Comprehensive utility toolkit:
- Data Management:
  - File loading and parsing
  - Results storage and retrieval
  - Directory management
- Name Generation:
  - Player names
  - Gamer tags
  - Team names
- AI Integration:
  - Yearly summary generation
  - Article writing
  - Context management
- Result Processing:
  - Data filtering
  - Format conversion
  - Text formatting

### Data Files (game/data/)
Contains all static data for the game:
- `first_names.txt`: 2942 possible first names
- `last_names.txt`: 158 possible last names
- `gamer_tags.txt`: 210 unique gamer tags
- `team_names.txt`: Regional team distribution:
  - Americas: 10 teams
  - Europe: 10 teams
  - China: 10 teams
  - Pacific: 10 teams

## Technical Details

### Match Simulation
- Uses skill-based probability system
- Implements realistic overtime rules
- Tracks detailed statistics
- Caches results for consistency

### Tournament Formats
- Regular Season: Round-robin
- Playoffs: Double-elimination
- World Championship:
  - Group Stage: Double-elimination groups
  - Knockout Stage: Double-elimination bracket

### Rating System
- Player skills: Normal distribution (mean 75, std 10)
- Team rating: Average of player skills
- Match probability: Skill difference based
- Rating tracking between seasons

### File Storage
- Results stored in `previous_results` directory
- Organized by year and competition
- Maintains complete match histories
- Supports AI summary generation

This README provides a comprehensive reference for understanding the game's architecture, components, and systems. Each section can be used as a quick reference for specific functionality or as a guide for modifications and enhancements.
