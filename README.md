# Fantasy Premier League Data 

Repository to download all available FPL Data; current and previous 
seasons. 

This repository will automatically update and save data to csv files that
can be downloaded from the 'Data' folder. 

Additionally, it contains optimisation models to support team selection, which 
can be accessed, downloaded and edited. 

For any assistance please contact: t.burnand@ucl.ac.uk

### **Details of code**

### 'Code.player'

This downloads all player information from the current gameweek only. 

Information:

  * Player ID
  * Name
  * Last_Name
  * Team
  * Position
  * Cost_Today
  * GW Points
  * Minutes
  * KO_time
  * Goals
  * Assists
  * Clean Sheets
  * Goals Conceded
  * Penalties Saved
  * Penalties Missed
  * YC
  * RC
  * Saves
  * Total Bonus Points
  * Total BPS
  * Influence
  * Creativity
  * Threat
  * ICT Index
  * xG (Expected goals)
  * xA (Expected assists)
  * xGi (Expected goal involvements)
  * xGc (Expected goals conceded)
  * Transfers In GW
  * Transfers Out GW
  * Gameweek
  * Opponent
  * Difficulty


### `Code.player_acc`

This downloads all accumulated player information up to and including current 
gameweek.

This file includes detailed information about upcoming fixtures and difficulty 
that is explained below. 

Note: xGi, xGc, GW_points, Transfers Out GW and Transfers in GW is specific 
to the gameweek. 

Information

  * Player ID
  * Name
  * Last_Name
  * Team
  * Position
  * Cost_Today
  * Total Points
  * Form
  * xGi (Expected goal involvements)
  * xGc (Expected goal conceded)
  * Points/Game
  * Selection %
  * Goals
  * Assists
  * Clean Sheets
  * GW Points
  * Total Bonus Points
  * Total BPS
  * Goals Conceded
  * Minutes
  * YC
  * RC
  * Saves
  * Penalties Saved
  * Penalties Missed
  * Transfers Out GW
  * Transfers In GW
  * Influence
  * Creativity
  * Threat
  * ICT Index
  * GW2 - Gameweek fixture 2 (Current gameweek - note this increases each GW). 
  * GW3 - Gameweek fixture 3
  * GW4 - Gameweek fixture 4
  * GW5 - etc.
  * GW6 - etc.
  * GW7 - etc.
  * CGW - Current gameweek difficulty (GW2 in this example)
  * NGW - Next gameweek difficulty (GW3 in this example)
  * NGW2 - Next, next gameweek difficulty (GW4 in this example)
  * NGW3 - etc.
  * NGW4 - etc.
  * NGW5 - etc.
  * Diff_Score_1_GW - Difficulty score for next gameweek
  * Diff_Score_2_GW - Combined difficulty score for next 2 gameweeks
  * Diff_Score_3_GW - Combined difficulty score for next 3 gameweeks
  * Diff_Score_4_GW - etc.
  * Diff_Score_5_GW - etc.
  * FDI_1 - Form / Diff_Score_1_GW
  * FDI_2 - Form / Diff_Score_2_GW
  * FDI_3 - etc.
  * FDI_4 - etc.
  * FDI_5 - etc.


### `Code.team`

This downloads all accumulated team data from FBRef website, including 
attacking and defensive. 

The full glossary can be found here:

https://fbref.com/en/comps/9/Premier-League-Stats


### `Code.load`

This module provides a single class: `FplApiDataRaw`

This class can be used to download all relevant data from the FPL API, including:
  * Elements (Players)
  * Element types (Positions)
  * Teams
  * Events (Game weeks)
  * Fixtures

To use the `FplApiDataRaw` class, first create an instance of the class:
```python
from Code.load import FplApiDataRaw

# make a request to the FPL API
data = FplApiDataRaw()
```
Then, you can access the data using the following attributes:
  * `elements_json`: A list of all players in the current season
  * `element_types_json`: A list of all positions in the FPL game
  * `teams_json`: A list of all teams in the Premier League
  * `events_json`: A list of all game weeks in the current season
  * `fixtures_json`: A list of all fixtures in the current season

### `Code.utils'

A small module to drop keys from a dictionary. 

### 1. Download the environment 
```bash
cd fantasy-premier-league
conda env create -f environment.yml
```

### 2. Activate the environment
```bash
conda activate FPL_Data
```

### Models and performance

Details of each model can be found in the folder 'Models' and their respective 
performance in 'Model Performance'. 

  * 'Model_1' uses a combination of form and fixture difficulty over a number of weeks. 

  *  'Model_2' is currently under development. 