# Generate report of Kanban board

# Description
These script is designed to generate report of Kanban board that helps PM or team member to keep track there own tasks.
The report generated is ...

# Installation
## Prerequisites
Python 3.10.11

## Steps
1. pip install -r requirements.txt


# How to use
## Steps
1. At the end of month, open Kanban board in browser and choose "Export plan to Excel"
2. Open the file that has just exported, and save as CSV UTF-8 (Comma delimited) (*.csv) with format "name of month this month" + "_" + "data" (ex: February_data.csv)
4. Move the file to /data folder
5. Run "generate.bat"
6. Generated result will appear at /report folder
