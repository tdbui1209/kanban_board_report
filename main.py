import pandas as pd
import os
from clean import concat_data
from plot import plot_pie_done, plot_pie_late, plot_num_tasks_by_department
from plot import plot_count_by_ytd, plot_num_tasks_by_mtd, plot_count_priority
import xlsxwriter
from datetime import datetime
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')


CREATED_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
COLUMN_DONE_TASKS = ['Task Name', 'Priority', 'Assigned To', 'Start Date', 'Due Date', 'Completed Date', 'Department', 'Gap']
COLUMN_NOT_DONE_TASKS = ['Task Name', 'Priority', 'Assigned To', 'Start Date', 'Due Date', 'Department', 'Remaining Days']


def overview_worksheet(workbook, data):
    """
    Generate overview worksheet
    """
    worksheet = workbook.add_worksheet('Overview')
    worksheet.write('A1', f'Created time: {CREATED_TIME}')

    # Number of tasks by progress and month
    plot_num_tasks_by_mtd(data, 'Bucket Name', 'Tasks of each bucket by MTD', 'report/num_tasks_by_progress_and_month.png')
    worksheet.insert_image('A4', 'report/num_tasks_by_progress_and_month.png')

    # Pie chart of percentage of done tasks
    plot_pie_done(data, 'Percentage of done tasks', 'report/pie_done.png')
    worksheet.insert_image('Q4', 'report/pie_done.png')

    # Pie chart of percentage of late tasks
    plot_pie_late(data, 'Percentage of late tasks', 'report/pie_late.png')
    worksheet.insert_image('Y4', 'report/pie_late.png')

    # Number of tasks by department
    plot_num_tasks_by_department(data, 'Tasks requested of department by MTD', 'report/num_tasks_by_department.png')
    worksheet.insert_image('A38', 'report/num_tasks_by_department.png')

    # Number of tasks by assigned team
    plot_num_tasks_by_mtd(data, 'Assigned Team', 'Tasks assigned to team by MTD', 'report/num_tasks_by_assigned_team.png')
    worksheet.insert_image('Q38', 'report/num_tasks_by_assigned_team.png')

    # Count of tasks each bucket by YTD
    plot_count_by_ytd(data, 'Bucket Name', 'Tasks of each bucket by YTD', 'report/count_tasks_by_bucket.png')
    worksheet.insert_image('A73', 'report/count_tasks_by_bucket.png')


def tasks_worksheet(workbook, data):
    """
    Generate tasks worksheet
    """
    worksheet = workbook.add_worksheet('Tasks')
    worksheet.write('A1', f'Created time: {CREATED_TIME}')

    # Pie chart of percentage of done tasks
    plot_pie_done(data, 'Percentage of done tasks', 'report/pie_done.png')
    worksheet.insert_image('A4', 'report/pie_done.png')

    # Pie chart of percentage of late tasks
    plot_pie_late(data, 'Percentage of late tasks', 'report/pie_late.png')
    worksheet.insert_image('K4', 'report/pie_late.png')

    # Write data to Tasks worksheet
    df_tasks = data.copy()
    df_tasks = df_tasks[df_tasks['Current Month'] == df_tasks['Current Month'].max()]

    df_tasks_done = df_tasks[df_tasks['Bucket Name'] == 'Done']
    df_tasks_done = df_tasks_done[COLUMN_DONE_TASKS]
    
    df_tasks_not_done = df_tasks[df_tasks['Bucket Name'] != 'Done']
    df_tasks_not_done = df_tasks_not_done[COLUMN_NOT_DONE_TASKS]

    worksheet.merge_range('A30:H30', 'Done Tasks', workbook.add_format({'bold': True, 'valign': 'vcenter', 'align': 'center'}))
    worksheet.write_row('A31', df_tasks_done.columns, workbook.add_format({'bold': True, 'border': 1}))
    for i in range(len(df_tasks_done)):
        for j in range(len(df_tasks_done.columns)):
            try:
                if df_tasks_done.iloc[i, 7] < pd.Timedelta(0):
                    worksheet.write(i+31, j, df_tasks_done.iloc[i][j], workbook.add_format({'bg_color': '#ff9999', 'border': 1}))
                else:
                    worksheet.write(i+31, j, df_tasks_done.iloc[i][j], workbook.add_format({'border': 1}))
                worksheet.set_column(j, j, 11)
            except Exception as e:
                pass
    
    avg_time = df_tasks_done['Gap'].mean().days
    worksheet.write(len(df_tasks_done)+31, len(df_tasks_done.columns)-2, 'Average:', workbook.add_format({'bold': True, 'border': 1}))
    if avg_time < 0:
        worksheet.write(len(df_tasks_done)+31, len(df_tasks_done.columns)-1,
            f'Overdue {avg_time} day(s)', workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#ff9999'}))
    else:
        worksheet.write(len(df_tasks_done)+31, len(df_tasks_done.columns)-1,
            f'Early {avg_time} day(s)', workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#9ACD32'}))

    worksheet.merge_range('K30:R30', f'Tasks Left: {len(df_tasks_not_done)}', workbook.add_format({'bold': True, 'valign': 'vcenter', 'align': 'center'}))
    worksheet.write_row('K31', df_tasks_not_done.columns, workbook.add_format({'bold': True, 'border': 1}))
    for i in range(len(df_tasks_not_done)):
        for j in range(len(df_tasks_not_done.columns)):
            try:
                if df_tasks_not_done.iloc[i, 6] < pd.Timedelta(0):
                    worksheet.write(i+31, j+10, df_tasks_not_done.iloc[i, j], workbook.add_format({'bg_color': '#ff9999', 'border': 1}))
                else:
                    worksheet.write(i+31, j+10, df_tasks_not_done.iloc[i, j], workbook.add_format({'border': 1}))
                worksheet.set_column(j+10, j+10, 11)
            except Exception as e:
                pass

    plot_count_priority(data, 'Number of tasks by priority', 'report/count_tasks_by_priority.png')
    worksheet.insert_image(f'A{len(df_tasks_not_done)+35}', 'report/count_tasks_by_priority.png')


def member_worksheet(workbook, data):
    for member in data['Assigned To'].unique():
        worksheet = workbook.add_worksheet(member)
        worksheet.write('A1', f'Created time: {CREATED_TIME}')

        member_data = data[data['Assigned To'] == member]
        member_data = member_data[member_data['Current Month'] == member_data['Current Month'].max()]
        member_data.dropna(subset=['Due Date'], inplace=True, ignore_index=True)

        plot_pie_done(member_data, f'Percentage of done tasks of {member}', f'report/pie_done_{member}.png')
        worksheet.insert_image('A4', f'report/pie_done_{member}.png')

        plot_pie_late(member_data, f'Percentage of late tasks of {member}', f'report/pie_late_{member}.png')
        worksheet.insert_image('K4', f'report/pie_late_{member}.png')

        member_data_done = member_data[member_data['Bucket Name'] == 'Done']
        member_data_not_done = member_data[member_data['Bucket Name'] != 'Done']

        member_data_done = member_data_done[COLUMN_DONE_TASKS]
        member_data_not_done = member_data_not_done[COLUMN_NOT_DONE_TASKS]
        
        worksheet.merge_range('A30:H30', 'Done Tasks', workbook.add_format({'bold': True, 'valign': 'vcenter', 'align': 'center'}))
        worksheet.write_row('A31', member_data_done.columns, workbook.add_format({'bold': True, 'border': 1}))

        for i in range(len(member_data_done)):
            for j in range(len(member_data_done.columns)):
                try:
                    if member_data_done.iloc[i, 7] < pd.Timedelta(0):
                        worksheet.write(i+31, j, member_data_done.iloc[i][j], workbook.add_format({'bg_color': '#ff9999', 'border': 1}))
                    else:
                        worksheet.write(i+31, j, member_data_done.iloc[i][j], workbook.add_format({'border': 1}))
                    worksheet.set_column(j, j, 11)
                except Exception as e:
                    pass

        avg_time = member_data_done['Gap'].mean().days
        worksheet.write(len(member_data_done)+31, len(member_data_done.columns)-2, 'Average:', workbook.add_format({'bold': True, 'border': 1}))
        if avg_time < 0:
            worksheet.write(len(member_data_done)+31, len(member_data_done.columns)-1,
                f'Overdue {avg_time} day(s)', workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#ff9999'}))
        else:
            worksheet.write(len(member_data_done)+31, len(member_data_done.columns)-1,
                f'Early {avg_time} day(s)', workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#9ACD32'}))

        format_red = workbook.add_format()
        format_red.set_bg_color('#ff9999')

        worksheet.merge_range('K30:R30', f'Tasks Left: {len(member_data_not_done)}', workbook.add_format({'bold': True, 'valign': 'vcenter', 'align': 'center'}))
        worksheet.write_row('K31', member_data_not_done.columns, workbook.add_format({'bold': True, 'border': 1}))

        for i in range(len(member_data_not_done)):
            for j in range(len(member_data_not_done.columns)):
                try:
                    if member_data_not_done.iloc[i, 6] < pd.Timedelta(0):
                        worksheet.write(i+31, j+10, member_data_not_done.iloc[i, j], workbook.add_format({'bg_color': '#ff9999', 'border': 1}))
                    else:
                        worksheet.write(i+31, j+10, member_data_not_done.iloc[i, j], workbook.add_format({'border': 1}))
                    worksheet.set_column(j+10, j+10, 11)
                except Exception as e:
                    pass
        
        plot_count_priority(member_data, f'Number of tasks by priority of {member}', f'report/count_tasks_by_priority_{member}.png')
        worksheet.insert_image(f'A{len(member_data_not_done)+35}', f'report/count_tasks_by_priority_{member}.png')


def summary(data, output_path):
    """
    Generate summary of the data
    """
    workbook = xlsxwriter.Workbook(f'{output_path}/IT Department.xlsx')

    with tqdm(total=3+len(data['Assigned Team'].unique()), desc='Generating summary') as pbar:
        # Overview worksheet
        overview_worksheet(workbook, data)
        pbar.update(1)

        # Tasks worksheet
        tasks_worksheet(workbook, data)
        pbar.update(1)

        pbar.set_description('Generating report')
        # Workbooks for each team
        teams = data['Assigned Team'].unique()
        for team in teams:
            team_data = data[data['Assigned Team'] == team]
            team_workbook = xlsxwriter.Workbook(f'{output_path}/{team}.xlsx')
            overview_worksheet(team_workbook, team_data)
            tasks_worksheet(team_workbook, team_data)

            # Workbooks for each member
            member_worksheet(team_workbook, team_data)
            team_workbook.close()

            pbar.update(1)

        # Remove images
        for item in os.listdir(output_path):
            if item.endswith('.png'):
                os.remove(os.path.join(output_path, item))
        pbar.update(1)


if __name__ == '__main__':
    total_data = concat_data()
    summary(total_data, 'report')
    