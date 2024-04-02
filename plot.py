import yaml
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
matplotlib.use('Agg')


CONFIG = yaml.load(open('config.yml'), Loader=yaml.FullLoader)
MONTHS = CONFIG['months']
COLORS = CONFIG['colors']


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
    temp = data[column].groupby(data['Start Month'], observed=True).value_counts().unstack()
    temp = temp.reindex(MONTHS, axis=0)
    temp.fillna(0, inplace=True)
    ax = temp.plot(kind='bar', stacked=True, figsize=(12, 8), color=COLORS)
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
    count_done = data[data['Bucket Name'] == 'Done'].shape[0]
    count_not_done = data[data['Bucket Name'] != 'Done'].shape[0]

    if count_not_done == 0:
        count_done = 1
    elif count_done == 0:
        count_done_not = 1
    ax = plt.figure(figsize=(8, 6))
    plt.pie([count_done, count_not_done],
            labels=['Done', 'Not done'], autopct='%1.1f%%',
            startangle=140, colors=["#5DE2E7", "#ff9999"])
    plt.title(title)
    plt.savefig(filename, bbox_inches='tight')


def plot_pie_late(data, title, filename):
    """
    Plot pie chart of percentage of late tasks
    """
    count_late = data[data['Bucket Name'] == 'Ongoing-Risky'].shape[0]
    count_not_late = data[~data['Bucket Name'].isin(['Ongoing-Risky', 'Done'])].shape[0]

    if count_late == 0:
        count_not_late = 1
    elif count_not_late == 0:
        count_late = 1
    ax = plt.figure(figsize=(8, 6))
    plt.pie([count_late, count_not_late], labels=['Late', 'Not late'], autopct='%1.1f%%',
            startangle=140, colors=["#ff9999", "#5DE2E7"])
    plt.title(title)
    plt.savefig(filename, bbox_inches='tight')



def plot_num_tasks_by_unit(data, title, filename):
    """
    Plot clustered stacked bar chart of number of tasks by unit
    """
    temp = data['Bucket Name'].groupby(data['Unit'], observed=True).value_counts().unstack()
    ax = temp.plot(kind='bar', stacked=True, figsize=(12, 8), color=COLORS)
    ax = display_num_of_columns(ax)
    plt.yticks(list(map(int, plt.yticks()[0])))
    plt.title(title)
    plt.xlabel('Unit')
    plt.ylabel('Number of tasks')
    plt.xticks(rotation=0)
    plt.yticks(list(map(int, plt.yticks()[0])))
    plt.savefig(filename, bbox_inches='tight')


def plot_count_by_ytd(data, column, title, filename):
    """
    Plot bar chart of count of tasks by column of current year to date
    """
    ax = plt.figure(figsize=(12, 8))
    ax = sns.countplot(y=column, data=data, palette=COLORS)
    ax = display_num_of_columns_horizontal(ax)
    plt.title(title)
    plt.ylabel(column)
    plt.xlabel('Number of tasks')
    plt.xticks(list(map(int, plt.xticks()[0])))
    plt.savefig(filename, bbox_inches='tight')
