## Setup

import pandas as pd
import numpy as np
# %matplotlib widget
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# import matplotlib.cbook as cbook
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

%matplotlib inline
# %matplotlib notebook
%matplotlib widget

import ranking as rk

## Import Data
results = pd.read_csv('Results_Composite.csv')

print(results.shape)

# Initiailize for All Ranking Types

ratingCoeff = {}
ratingCoeff['simpleElo'] = {'initRating' : 1500, 
                            'avgRating' : 1500,
                            'kRating' : 30,
                            'regress' : 0,
                            'hfAdvantage': 0,
                            'goalDiffExp': 0}

ratingCoeff['basicElo'] = {'initRating' : 1300, 
                           'avgRating' : 1500,
                           'kRating' : 30,
                           'regress' : 0.3,
                           'hfAdvantage': 0,
                           'goalDiffExp': 0}

ratingCoeff['hfAdvElo'] = {'initRating' : 1300, 
                           'avgRating' : 1500,
                           'kRating' : 30,
                           'regress' : 0.3,
                           'hfAdvantage': 30,
                           'goalDiffExp': 0}

ratingCoeff['fullElo'] = {'initRating' : 1300, 
                          'avgRating' : 1500,
                          'kRating' : 30,
                          'regress' : 0.3,
                          'hfAdvantage': 30,
                          'goalDiffExp': 0.2}

# print(list(ratingCoeff.keys()))

for rankingType in list(ratingCoeff.keys()):
    results[rankingType + ' Away'] = np.nan
    results[rankingType + ' Home'] = np.nan
    results[rankingType + ' Error'] = np.nan
    
## Run single rankings
# rankingType = 'simpleElo'
rankingType = ['basicElo']

results, rankingDict = rk.gameRanking(results, ratingCoeff, rankingType)

## Plot Error of each game
rankingMethod = rankingType[0]

# https://matplotlib.org/3.1.1/gallery/text_labels_and_annotations/date.html
years = mdates.YearLocator(10)   # every year, https://matplotlib.org/3.1.1/api/dates_api.html#matplotlib.dates.YearLocator
months = mdates.MonthLocator()  # every month
years_fmt = mdates.DateFormatter('%Y')

fig, ax = plt.subplots()
# plt.plot(results['Date'], results['simpleElo Error'],'.')
# ax.plot('Date', 'simpleElo Error', data = results)
dates = results['Date'].to_numpy(dtype = 'datetime64[ns]')
ax.plot(dates, results[rankingMethod + ' Error'],'.')

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

ax.set(xlabel = 'Date', ylabel = 'Square Error')

# rotates and right aligns the x labels, and moves the bottom of the
# axes up to make room for them
fig.autofmt_xdate()

plt.show()

## Plot Boxplot of error for each season
rankingMethod = rankingType[0]
# rankingMethod = 'basicElo'

# results.groupby('Season').boxplot([rankingMethod + ' Error'])
# results.groupby('Season')
# print(results.groupby('Season').mean()['basicElo Error'])

plt.plot(results.groupby('Season').median()[rankingMethod + ' Error'])
plt.plot(results.groupby('Season').mean()[rankingMethod + ' Error'])

# results.boxplot(column = [rankingMethod + ' Error'], by = 'Season')

plt.figure()
plt.plot(results.groupby('Season').count()[rankingMethod + ' Error'])

## Iterate rankings through K values
allTeams = findTeams(results)
rankingDict = rankingsInit(allTeams, initEloSimple)
eloError = pd.DataFrame(columns = ['k', 'Elo_Error'])

for k in range(10,60,10):
    results, rankingDict = gameRanking(results, rankingDict, k)
#     print(k)    
    averageError = results['simpleElo Error'].mean()
#     print(averageError)
    eloError = eloError.append({'k':k, 'Elo_Error':averageError}, ignore_index=True)

eloError.plot(x = 'k', y = 'Elo_Error')

minErroridx = eloError['Elo_Error'].idxmin()
minError =  eloError['Elo_Error'][minErroridx]
minErrork = eloError['k'][minErroridx]
plt.plot(minErrork, minError, 'o')
plt.annotate('Min Error: ' + str(minErrork), 
            xy = (minErrork, minError),
            xytext = (minErrork, minError + 0.01))

plt.show()

from scipy.optimize import minimize
from importlib import reload
reload(rk)

def optimizeElo(results, ratingCoeff, rankingType):
    results, rankingDict = rk.gameRanking(results, ratingCoeff, rankingType)
    errorCol = rankingType[0] + ' Error'
    print(errorCol)
    eloErrorList = results[results.Season > 2010]
    print(eloErrorList.columns)
    eloErrorMedian = eloErrorList[errorCol].median()
    print(eloErrorList.shape)
    print(eloErrorMedian)
    print(eloErrorList[errorCol])
    
#     eloErrorList = results[results.Season > 2015]
#     eloErrorMedian = eloErrorList[errorCol].median()
#     print(eloErrorList.shape)
#     print(eloErrorMedian)

## Import Data
results = pd.read_csv('Results_Composite.csv')

resultsShrink = results[results.Season > 2010]

print(results.shape)
print(resultsShrink.shape)

ratingCoeff = {}

ratingCoeff['basicElo'] = {'initRating' : 1300, 
                           'avgRating' : 1500,
                           'kRating' : 30,
                           'regress' : 0.3,
                           'hfAdvantage': 0,
                           'goalDiffExp': 0}

rankingType = ['basicElo']

# print(resultsShrink.iterrows())

# for row in resultsShrink.itertuples(index=False):
# for index, row in enumerate(resultsShrink.itertuples(index=False)):
# #     season = resultsShrink.Season[row]
# #     print('Index: ' + str(row) + '  Season: ' + str(season))
#     print('Index: ' + str(index))

optimizeElo(resultsShrink, ratingCoeff, rankingType)
