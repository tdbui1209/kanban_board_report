from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
matplotlib.use('Agg')


MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
          'November', 'December']


def display_num_of_columns(ax):
    """
    Display number of tasks on middle of each bar
    """
    for p in ax.patches:
        if p.get_height() > 0:
            ax.annotate(str(int(p.get_height())), (p.get_x() + p.get_width() / 2, p.get_y() + p.get_height() / 2),
                        ha='center', va='bottom')
    return ax
            

def plot_num_tasks_by_mtd(data, column, title, filename):
    """
    Plot clustered stacked bar chart of number of tasks by month and column
    """
    temp = data[column].groupby(data['Current Month'], observed=True).value_counts().unstack()
    temp = temp.reindex(MONTHS, axis=0)
    temp.fillna(0, inplace=True)
    ax = temp.plot(kind='bar', stacked=True, colormap='Set2', figsize=(12, 8))
    ax = display_num_of_columns(ax)
    ax.set_yticks(list(map(int, ax.get_yticks())))
    ax.title.set_text(title)
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of tasks')
    ax.set_xticklabels(MONTHS, rotation=0)
    ax.figure.savefig(filename, bbox_inches='tight')


def plot_pie_done(data, title, filename):
    """
    Plot pie chart of percentage of done tasks
    """
    temp = data[data['Current Month'] == data['Current Month'].max()]
    temp.dropna(subset=['Due Date'], inplace=True, ignore_index=True)
    count_done = temp[temp['Bucket Name'] == 'Done'].shape[0]
    count_not_done = temp[temp['Bucket Name'] != 'Done'].shape[0]
    try:
        ax = plt.figure(figsize=(8, 6))
        plt.pie([count_done, count_not_done],
                labels=['Done', 'Not done'], autopct='%1.1f%%',
                startangle=140, colors=['#66b3ff', '#ff9999'])
        plt.title(title)
        plt.savefig(filename, bbox_inches='tight')
    except Exception as e:
        pass


def plot_pie_late(data, title, filename):
    """
    Plot pie chart of percentage of late tasks
    """
    temp = data[data['Current Month'] == data['Current Month'].max()]
    temp.dropna(subset=['Due Date'], inplace=True, ignore_index=True)

    temp_done = temp[temp['Bucket Name'] == 'Done']
    temp_not_done = temp[temp['Bucket Name'] != 'Done']
    temp_done['Gap'] = temp_done['Due Date'].astype('datetime64[ns]') - temp_done['Completed Date'].astype('datetime64[ns]')
    temp_done['Gap'] = temp_done['Gap'].dt.days.apply(lambda x: pd.Timedelta(x, unit='D'))
    count_late_done = temp_done['Gap'].apply(lambda x: 1 if x.days < 0 else 0).sum()

    temp_not_done['Remaining Time'] = temp_not_done['Due Date'].astype('datetime64[ns]').dt.date - datetime.now().date()
    temp_not_done['Remaining Time'] = temp_not_done['Remaining Time'].apply(lambda x: pd.Timedelta(x, unit='D'))
    count_late_not_done = temp_not_done['Remaining Time'].apply(lambda x: x.days).apply(lambda x: 1 if x < 0 else 0).sum()

    count_late = count_late_done + count_late_not_done
    count_not_late = temp.shape[0] - count_late
    try:
        ax = plt.figure(figsize=(8, 6))
        plt.pie([count_late, count_not_late], labels=['Late', 'Not late'], autopct='%1.1f%%',
                startangle=140, colors=['#ff9999', '#66b3ff'])
        plt.title(title)
        plt.savefig(filename, bbox_inches='tight')
    except Exception as e:
        pass


def plot_num_tasks_by_department(data, title, filename):
    """
    Plot clustered stacked bar chart of number of tasks by department of current month
    """
    temp = data[data['Current Month'] == data['Current Month'].max()]
    temp = temp['Bucket Name'].groupby(temp['Department'], observed=True).value_counts().unstack()
    ax = temp.plot(kind='bar', stacked=True, colormap='Set2', figsize=(12, 8))
    ax = display_num_of_columns(ax)
    plt.yticks(list(map(int, plt.yticks()[0])))
    plt.title(title)
    plt.xlabel('Department')
    plt.ylabel('Number of tasks')
    plt.xticks(rotation=0)
    plt.savefig(filename, bbox_inches='tight')


def plot_count_by_ytd(data, column, title, filename):
    """
    Plot bar chart of count of tasks by column of current year to date
    """
    temp = data[data['Current Month'] == data['Current Month'].max()]
    ax = plt.figure(figsize=(12, 8))
    sns.countplot(data=temp, y=column, palette='Set2')
    plt.title(title)
    plt.ylabel(column)
    plt.xlabel('Number of tasks')
    plt.xticks(list(map(int, plt.xticks()[0])))
    ax = display_num_of_columns(ax)
    plt.savefig(filename, bbox_inches='tight')
