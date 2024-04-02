import pandas as pd
import os
import xlsxwriter
from datetime import datetime
from tqdm import tqdm
import yaml
from tkinter import filedialog as fd

from clean import clean
from plot import plot_pie_done, plot_pie_late, plot_num_tasks_by_unit
from plot import plot_count_by_ytd, plot_num_tasks_by_mtd

import warnings
warnings.filterwarnings('ignore')


CREATED_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
COLUMN_DONE_TASKS = ['Task Name', 'Priority', 'Assigned To', 'Start Date', 'Due Date', 'Completed Date', 'Unit']
COLUMN_NOT_DONE_TASKS = ['Task Name', 'Priority', 'Assigned To', 'Start Date', 'Due Date', 'Unit', 'Remaining Days']


def create_charts(worksheet, data, output_path, suffix):
    """
    Create charts in worksheet
    """
    # Number of tasks by progress and month
    plot_num_tasks_by_mtd(data, 'Bucket Name', 'Tasks of each bucket by MTD', f'{output_path}/num_tasks_by_progress_and_month_{suffix}.png')
    worksheet.insert_image('A4', f'{output_path}/num_tasks_by_progress_and_month_{suffix}.png')

    # Pie chart of percentage of done tasks
    plot_pie_done(data, 'Percentage of done tasks', f'{output_path}/pie_done_{suffix}.png')
    worksheet.insert_image('Q4', f'{output_path}/pie_done_{suffix}.png')

    # Pie chart of percentage of late tasks
    plot_pie_late(data, 'Percentage of late tasks', f'{output_path}/pie_late_{suffix}.png')
    worksheet.insert_image('Y4', f'{output_path}/pie_late_{suffix}.png')

    # Number of tasks by unit
    plot_num_tasks_by_unit(data, 'Tasks requested of unit by YTD', f'{output_path}/num_tasks_by_unit_{suffix}.png')
    worksheet.insert_image('A38', f'{output_path}/num_tasks_by_unit_{suffix}.png')

    # Count of tasks each bucket by YTD
    plot_count_by_ytd(data, 'Bucket Name', 'Tasks of each bucket by YTD', f'{output_path}/count_tasks_by_bucket_{suffix}.png')
    worksheet.insert_image('AG4', f'{output_path}/count_tasks_by_bucket_{suffix}.png')


def create_tasks_table(worksheet, workbook, data):
    """
    Create table of tasks in worksheet
    """
    df_tasks_done = data[data['Bucket Name'] == 'Done']
    df_tasks_done = df_tasks_done[COLUMN_DONE_TASKS]
    
    df_tasks_not_done = data[data['Bucket Name'] != 'Done']
    df_tasks_not_done = df_tasks_not_done[COLUMN_NOT_DONE_TASKS]

    create_table(worksheet, workbook, df_tasks_done, f'Done Tasks: {len(df_tasks_done)}', 'Q', 30)
    create_table(worksheet, workbook, df_tasks_not_done, f'Left Tasks: {len(df_tasks_not_done)}', 'Y', 30)


def create_table(worksheet, workbook, data, title, start_col, start_row):
    """
    Create table in worksheet
    """
    end_col = chr(ord(start_col) + len(data.columns) - 1)
    if end_col[-1] > 'Z':
        end_col = end_col[:-1] + 'A' + chr(ord(end_col[-1]) % ord('Z') + ord('A') - 1)

    worksheet.merge_range(f'{start_col}{start_row}:{end_col}{start_row}', title, workbook.add_format({'bold': True, 'valign': 'vcenter', 'align': 'center'}))
    worksheet.write_row(f'{start_col}{start_row+1}', data.columns, workbook.add_format({'bold': True, 'border': 1}))
    for i in range(len(data)):
        for j in range(len(data.columns)):
            try:
                if start_col[-1] > 'Z':
                    start_col = start_col[:-1] + 'A' + chr(ord(start_col[-1]) % ord('Z') + ord('A') - 1)
                worksheet.write(i+start_row+1, j+ord(start_col)-ord('A'), data.iloc[i][j], workbook.add_format({'border': 1}))
                if data.iloc[i, 6] < pd.Timedelta(0):
                    worksheet.write(i+start_row+1, j+ord(start_col)-ord('A'), data.iloc[i][j], workbook.add_format({'bg_color': '#ff9999', 'border': 1}))
                else:
                    worksheet.write(i+start_row+1, j+ord(start_col)-ord('A'), data.iloc[i][j], workbook.add_format({'border': 1}))
                worksheet.set_column(j+ord(start_col)-ord('A'), j+ord(start_col)-ord('A'), 11)
            except Exception as e:
                pass


def overview_worksheet(workbook, data, output_path, worksheet_title='Overview'):
    """
    Generate summary worksheet
    """
    worksheet = workbook.add_worksheet(worksheet_title)
    worksheet.write('A1', f'Created time: {CREATED_TIME}')

    create_charts(worksheet, data, output_path, worksheet_title)
    create_tasks_table(worksheet, workbook, data)


def summary(data):
    """
    Generate summary of the data
    """
    OUTPUT_PATH = 'report' + f'/W{datetime.now().isocalendar().week}'
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    workbook = xlsxwriter.Workbook(f'{OUTPUT_PATH}/HPH IT Department.xlsx')

    with tqdm(total=1+len(data['Assigned Team'].unique()), desc='Generating summary') as pbar:
        # Overview worksheet
        overview_worksheet(workbook, data, OUTPUT_PATH)
        pbar.update(1)

        workbook.close()
        # Workbooks for each team
        teams = data['Assigned Team'].unique()
        for team in teams:
            team_data = data[data['Assigned Team'] == team]
            team_workbook = xlsxwriter.Workbook(f'{OUTPUT_PATH}/{team}.xlsx')
            overview_worksheet(team_workbook, team_data, OUTPUT_PATH)
            
            for team_member in team_data['Assigned To'].unique():
                overview_worksheet(team_workbook, team_data[team_data['Assigned To'] == team_member], OUTPUT_PATH, team_member)
            team_workbook.close()

            pbar.update(1)

        # Remove temp chart images
        for item in os.listdir(OUTPUT_PATH):
            if item.endswith('.png'):
                os.remove(os.path.join(OUTPUT_PATH, item))
        pbar.update(1)


if __name__ == '__main__':
    config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)
    data = clean(fd.askopenfilename())
    summary(data)
