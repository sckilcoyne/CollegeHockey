# -*- coding: utf-8 -*-
"""
Plot ranking reusults.

Created on Sun Jul 19 11:31:12 2020

@author: Scott
"""

# Import standard modules
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
# import matplotlib.cbook as cbook

# Import custom modules
import Rankings as rk


def drop_suffix(self, suffix):
    self.columns = self.columns.str.replace(suffix+r'$', '')
    return self


pd.core.frame.DataFrame.drop_suffix = drop_suffix


def drop_prefix(self, prefix):
    self.columns = self.columns.str.replace(r'$'+prefix, '')
    return self


pd.core.frame.DataFrame.drop_prefix = drop_prefix


# Plot Error of each game
def plot_error_games(results, rankingMethod):
    # rankingMethod = rankingType[0]

    # https://matplotlib.org/3.1.1/gallery/text_labels_and_annotations/date.html
    years = mdates.YearLocator(10)   # every year
    # https://matplotlib.org/3.1.1/api/dates_api.html#matplotlib.dates.YearLocator
    # months = mdates.MonthLocator()  # every month
    years_fmt = mdates.DateFormatter('%Y')

    fig, ax = plt.subplots()
    # plt.plot(results['Date'], results['simpleElo Error'],'.')
    # ax.plot('Date', 'simpleElo Error', data = results)
    dates = results['Date'].to_numpy(dtype='datetime64[ns]')
    ax.plot(dates, results[rankingMethod + ' Error'], '.')

    # format the ticks
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(years_fmt)
    # ax.xaxis.set_minor_locator(months)
    # ax.locator_params(axis='x',nbins=10)

    # round to nearest years.
    datemin = np.datetime64(results['Date'][0], 'Y')
    datemax = np.datetime64(np.datetime64(
        results['Date'].iloc[-1], 'Y') + np.timedelta64(1, 'Y'))
    ax.set_xlim(datemin, datemax)

    # format the coords message box
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.grid(True)

    ax.set(xlabel='Date', ylabel='Square Error')

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()

    plt.show()


def plot_error_seasons(results, rankingMethod):
    # Plot Boxplot of error for each season
    # rankingMethod = rankingType[0]
    # rankingMethod = 'basicElo'

    # results.groupby('Season').boxplot([rankingMethod + ' Error'])
    # results.groupby('Season')
    # print(results.groupby('Season').mean()['basicElo Error'])

    plt.plot(results.groupby('Season').median()[rankingMethod + ' Error'])
    plt.plot(results.groupby('Season').mean()[rankingMethod + ' Error'])

    # results.boxplot(column = [rankingMethod + ' Error'], by = 'Season')

    plt.figure()
    plt.plot(results.groupby('Season').count()[rankingMethod + ' Error'])


# Plot ratings for a team over time
def plot_team_results(teamGames, overallMetrics, team='Northeastern', savePlot=False):

    # Get list of ranking types
    rankMethod = list(teamGames)
    del rankMethod[0]  # Remove Season column
    rankMethod = rankMethod[0]

    # Create figure
    # One plot for each ranking method
    seasonCount = teamGames.Season.max()-teamGames.Season.min()
    fig, axs = plt.subplots(len(rankMethod), seasonCount,
                            squeeze=False, sharey=True)
    fig.subplots_adjust(wspace=0.05)  # adjust space between axes
    fig.suptitle(team, fontweight='bold', fontsize=16)

    seasonGames = teamGames.groupby('Season')

    # Make each ranking system use same color but allow intra-season gaps
    cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
    custom_lines = []

    # Plot each ranking system by season
    # Markers for indiviual game ranking (post game)
    # Rolling average line of ranking
    for i, ax in enumerate(axs.flat):  # Subplot for each ranking method
        # https://stackoverflow.com/questions/20288842/matplotlib-iterate-subplot-axis-array-through-single-list
        for key, item in seasonGames:
            # color = cycle[i]
            color = cycle[0]
# =============================================================================
#             ax.scatter(
#                 item.index, item[rankMethod[i]], color=color,
#                 marker='x', alpha=0.3)
# =============================================================================
            ax.plot(item.index,
                    # item[rankMethod[i]].rolling('7d').mean(), color=color)
                    item[rankMethod].rolling('7d').mean(), color=color)
            custom_lines = custom_lines + [Line2D([0], [0], color=color)]

            # Add overall metrics for season
            seasonStart = item.index.min()
            seasonEnd = item.index.max()
# =============================================================================
#             seasonMax = overallMetrics.loc[(
#                 key, 'Average'), (rankMethod[i], 'seasonMax')]
#             seasonMin = overallMetrics.loc[(
#                 key, 'Average'), (rankMethod[i], 'seasonMin')]
#             seasonMean = overallMetrics.loc[(
#                 key, 'Average'), (rankMethod[i], 'seasonMean')]
# =============================================================================
            seasonMax = overallMetrics.loc[(
                key, 'Average'), (rankMethod, 'seasonMax')]
            seasonMin = overallMetrics.loc[(
                key, 'Average'), (rankMethod, 'seasonMin')]
            seasonMean = overallMetrics.loc[(
                key, 'Average'), (rankMethod, 'seasonMean')]
            ax.hlines(seasonMax, seasonStart, seasonEnd,
                      color=cycle[1], linestyles='dotted')
            ax.hlines(seasonMin, seasonStart, seasonEnd,
                      color=cycle[1], linestyles='dotted')
            ax.hlines(seasonMean, seasonStart, seasonEnd,
                      color=cycle[1], linestyles='dotted')

        # Label subplot
        # ax.set_title(rankMethod[i])

    # https://matplotlib.org/3.1.1/gallery/text_labels_and_annotations/custom_legends.html
    # ax.legend(custom_lines, rankMethod)

    # Create pretty date axis
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    # Set figure size
    # fig.set_figheight(2*len(rankMethod))
    fig.set_figheight(8)
    fig.set_figwidth(max(16, seasonCount))
    plt.tight_layout()

    # Add source refs
    plt.figtext(
        0.1, 1,
        '\ngithub.com/sckilcoyne/CollegeHockey\nGame results from CHN.com',
        verticalalignment='top')

    if savePlot:
        figTitle = 'Rating_allTime_' + team
        save_plot(fig, figTitle)
        plt.close(fig)


# Plot every team's all time rankings
def plot_all_team_results(results, rankingDict, overallMetrics):
    for team in rankingDict:
        # Only plot teams with above threshold number of games
        gameThreshold = 10
        if rankingDict[team]['gameCount'] > gameThreshold:
            teamGames = rk.team_games(results, team)
            plot_team_results(teamGames, overallMetrics, team, True)
    print('Plotted each team\'s all time results')


# Save plot to plot folder
def save_plot(fig, figTitle):
    pwd = os.getcwd()
    figFolder = pwd + '/Plots/'
    fig.savefig(figFolder+figTitle+'.png')
