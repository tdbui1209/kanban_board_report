import json
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
matplotlib.use('Agg')


CONFIG = json.load(open('config.json'))
MONTHS = CONFIG['months']


def display_num_of_columns(ax):
    """
    Display number of tasks on middle of each bar
    """
    for p in ax.patches:
        if p.get_height() > 0:
            ax.annotate(str(int(p.get_height())), (p.get_x() + p.get_width() / 2, p.get_y() + p.get_height() / 2),
                        ha='center', va='bottom')
    return ax


def display_num_of_columns_horizontal(ax):
    """
    Display number of tasks on top of each bar
    """
    for p in ax.patches:
        if p.get_width() > 0:
            ax.annotate(str(int(p.get_width())), (p.get_width() / 2, p.get_y() + p.get_height() / 2),
                        ha='left', va='center')
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
    count_late = temp[temp['Late'] == True].shape[0]
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
    plt.yticks(list(map(int, plt.yticks()[0])))
    plt.savefig(filename, bbox_inches='tight')


def plot_count_by_ytd(data, column, title, filename):
    """
    Plot bar chart of count of tasks by column of current year to date
    """
    temp = data[data['Current Month'] == data['Current Month'].max()]
    ax = plt.figure(figsize=(12, 8))
    ax = sns.countplot(y=column, data=temp, palette='Set2')
    ax = display_num_of_columns_horizontal(ax)
    plt.title(title)
    plt.ylabel(column)
    plt.xlabel('Number of tasks')
    plt.xticks(list(map(int, plt.xticks()[0])))
    plt.savefig(filename, bbox_inches='tight')


def plot_count_priority(data, title, filename):
    """
    Plot bar chart of count of tasks by priority of current month
    """
    temp = data[data['Current Month'] == data['Current Month'].max()]
    temp = temp['Late'].groupby(temp['Priority']).value_counts().unstack()
    temp.fillna(0, inplace=True)
    ax = temp.plot(kind='bar', stacked=True, figsize=(8, 6), color=['#66b3ff', '#ff9999'])
    ax = display_num_of_columns(ax)
    plt.title(title)
    plt.xlabel('Priority')
    plt.ylabel('Number of tasks')
    plt.xticks(rotation=0)
    plt.yticks(list(map(int, plt.yticks()[0])))
    plt.savefig(filename, bbox_inches='tight')
