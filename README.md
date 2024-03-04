# Generate report of Kanban board

# Description
These script is designed to generate report of Kanban board that helps PM or team member to keep track there own tasks.
The report generated is ...

# Installation
## Prerequisites
Python 3.10.11

## Steps
1. Install python 3.10.11
2. Clone this repos
   ```git clone https://github.com/tdbui1209/kanban_board_report.git```
3. Change directory
   ```cd kanban_board_report```
4. Create virtual enviroment
   ```python -m venv venv
5. Install nessesarry packages
   ```pip install -r requirements.txt```

# How to use
## Steps
1. At the end of month, open Kanban board in browser and choose "Export plan to Excel"
2. Open the file that has just exported, and save as CSV UTF-8 (Comma delimited) (*.csv) with format "name of month this month" + "_" + "data" (ex: February_data.csv)
4. Move the file to /data folder
5. Run "generate.bat"
6. Generated result will appear at /report folder
