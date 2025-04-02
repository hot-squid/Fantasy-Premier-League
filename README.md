# Fantasy Premier League Data 

Repository to download all available FPL Data; current and previous 
seasons. 

This repository will automatically update and save data to csv files that
can be downloaded from the 'Data' folder. 

Additionally, it contains optimisation models to support team selection, which 
can be accessed, downloaded and edited. 

For any assistance please contact: thomas.burnand@outlook.com

### **Details of code**

### `Code.player`

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

### `Code.utils`

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