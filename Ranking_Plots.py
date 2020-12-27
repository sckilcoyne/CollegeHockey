# -*- coding: utf-8 -*-
"""
Plot ranking reusults.

Created on Sun Jul 19 11:31:12 2020

@author: Scott
"""
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# import matplotlib.cbook as cbook


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
def team_rating(teamGames, team='Northeastern', savePlot=True):
    fig, ax = plt.subplots(1, 1)

    cols = list(teamGames)
    del cols[0]  # Remove Date column

    dateSeries = teamGames.index.to_pydatetime()

    ax.scatter(dateSeries, teamGames)

    # for col in cols:
    #     ax.scatter(dateSeries, teamGames[col])
    ax.plot(dateSeries, teamGames.rolling('7d').mean())
    ax.set_title(team)
    ax.legend(cols)

    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    if savePlot:
        figTitle = 'Rating_allTime_'+team
        save_plot(fig, figTitle)

# Collect all games by given team


def team_games(results, team='Northeastern'):

    awayCol = ([col for col in results.columns if '_Away' in col])
    homeCol = ([col for col in results.columns if '_Home' in col])

    awayGames = results.loc[results['Away'] == team, ['Date']+awayCol]
    homeGames = results.loc[results['Home'] == team, ['Date']+homeCol]

    awayGames = awayGames.drop_suffix('_Away')
    homeGames = homeGames.drop_suffix('_Home')

    teamGames = awayGames.append(homeGames)

    teamGames['Date'] = pd.to_datetime(teamGames['Date'], format='%Y-%m-%d')
    teamGames = teamGames.sort_values(by='Date')

    teamGames = teamGames.set_index('Date')

    return teamGames


def save_plot(fig, figTitle):
    pwd = os.getcwd()
    figFolder = pwd+'/Plots/'
    fig.savefig(figFolder+figTitle+'.png')
