import pandas as pd
import re
from pandas.api.types import CategoricalDtype
from datetime import datetime
import os
import json


CONFIG = json.load(open('config.json'))
TEAMS = CONFIG['teams']
BUCKET_CATEGORIES = CONFIG['bucket_categories']
PROGRESS_CATEGORIES = CONFIG['progress_categories']
PRIORITY_CATEGORIES = CONFIG['priority_categories']
MONTHS = CONFIG['months']


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
    data = data[data['Bucket Name'].isin(BUCKET_CATEGORIES)]
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
        team = re.findall(r"\[.*?\]", data['Task Name'][i])
        if len(team) == 0:
            assigned_team.append('Not assigned')
        else:
            if team[0][1:-1] not in TEAMS:
                assigned_team.append('Not assigned')
            else:
                assigned_team.append(team[0][1:-1])

    data['Assigned Team'] = assigned_team
    data = data[data['Assigned Team'] != 'Not assigned']
    data['Current Month'] = current_month
    return data


def concat_data():
    total_data = pd.DataFrame()
    for file in os.listdir('data'):
        if file.endswith('.csv'):
            temp_data = clean(f'data/{file}', file.split('_')[0])
            total_data = pd.concat([total_data, temp_data], ignore_index=True)
    total_data['Current Month'] = total_data['Current Month'].astype(CategoricalDtype(categories=MONTHS, ordered=True))
    total_data.to_csv('data/total_data.csv', index=False)
    return total_data
