# -*- coding: utf-8 -*-
"""
Plot ranking reusults.

Created on Sun Jul 19 11:31:12 2020

@author: Scott
"""
# import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# import matplotlib.cbook as cbook


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
    datemax = np.datetime64(np.datetime64(results['Date'].iloc[-1], 'Y') + np.timedelta64(1, 'Y'))
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
