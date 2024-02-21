import pandas as pd
import re
from pandas.api.types import CategoricalDtype
from datetime import datetime


TEAMS = ['Infra', 'MES', 'IT Admin']
BUCKET_CATEGORIES = ['Ongoing', 'Ongoing-Risky', 'Monitoring', 'Testing', 'Done']
PROGRESS_CATEGORIES = ['Not started', 'In progress', 'Completed']
PRIORITY_CATEGORIES = ['Medium', 'Important', 'Urgent']
PATTERN = r"\[.*?\]"
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
          'November', 'December']


def clean(data_path, current_month):
    data = pd.read_csv(data_path)
    data.drop(['Task ID', 'Checklist Items', 'Completed Checklist Items', 'Description'], axis=1, inplace=True)
    data['Start Date'].fillna(data['Created Date'], inplace=True)
    data['Assigned To'] = data['Assigned To'].str.split(';', expand=True)[0]
    data['Assigned To'].fillna('Not assigned', inplace=True)
    data['Assigned To'] = data['Assigned To'].astype('category')
    data['Created By'] = data['Created By'].astype('category')
    data['Completed By'] = data['Completed By'].astype('category')
    data['Labels'].fillna('Not assigned', inplace=True)
    data['Labels'] = data['Labels'].astype('category')
    data['Bucket Name'] = data['Bucket Name'].astype(CategoricalDtype(categories=BUCKET_CATEGORIES, ordered=True))
    data['Progress'] = data['Progress'].astype(CategoricalDtype(categories=PROGRESS_CATEGORIES, ordered=True))
    data['Priority'] = data['Priority'].astype(CategoricalDtype(categories=PRIORITY_CATEGORIES, ordered=True))
    data['Department'] = data['Labels'].copy()
    data.drop('Labels', axis=1, inplace=True)
    data.dropna(subset=['Bucket Name'], inplace=True, ignore_index=True)
    data.dropna(subset=['Due Date'], inplace=True, ignore_index=True)
    data.drop('Late', axis=1, inplace=True)
    data['Gap'] = data['Due Date'].astype('datetime64[ns]') - data['Completed Date'].astype('datetime64[ns]')
    data['Remaining Days'] = data['Due Date'].astype('datetime64[ns]').dt.date - datetime.now().date()
    
    for col, row in data.iterrows():
        if row['Bucket Name'] == 'Done':
            if row['Gap'].days < 0:
                data.at[col, 'Late'] = True
            else:
                data.at[col, 'Late'] = False
        else:
            if row['Remaining Days'].days < 0:
                data.at[col, 'Late'] = True
            else:
                data.at[col, 'Late'] = False

    
    assigned_team = []
    for i in range(len(data)):
        team = re.findall(PATTERN, data['Task Name'][i])
        if len(team) == 0:
            assigned_team.append('Not assigned')
        else:
            if team[0][1:-1] not in TEAMS:
                assigned_team.append('Not assigned')
            else:
                assigned_team.append(team[0][1:-1])

    data['Assigned Team'] = assigned_team
    data['Current Month'] = current_month
    return data


def concat_data():
    january_data = clean('data/January_data.csv', 'January')
    february_data = clean('data/February_data.csv', 'February')
    total_data = pd.concat([january_data, february_data], ignore_index=True)
    total_data['Current Month'] = total_data['Current Month'].astype(CategoricalDtype(categories=MONTHS, ordered=True))
    total_data.to_csv('data/total_data.csv', index=False)
    return total_data
