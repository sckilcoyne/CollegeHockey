# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 12:54:00 2021

@author: Scott
"""

# %% Setup
# Import common modules
import pandas as pd
import importlib
import matplotlib.pyplot as plt
import streamlit as st
import requests
import json
import matplotlib.dates as mdates

# Import custom modules
import rankings as rk
import Ranking_Plots as rkplt
import Ranking_Coefficients
import Import_Results as ir

debug = [False, True, 'verbose']

rankMethod = 'fullElo'

# %% Set up data


@st.cache
def import_from_github():
    # Github data sources
    githubRepo = 'https://raw.githubusercontent.com/sckilcoyne/CollegeHockey/'
    githubBranch = 'master/'
    githubURL = githubRepo + githubBranch

    rankingDictFile = githubURL + 'Ranking_Dict.txt'
    rankingResultsFile = githubURL + 'Results_Rankings.csv'
    compositeResultsFile = githubURL + 'Results_Composite.csv'
    overallMetricsFile = 'https://github.com/sckilcoyne/CollegeHockey/blob/master/Overall_Metrics.h5?raw=true'

    # Import data
    r = requests.get(overallMetricsFile, allow_redirects=True)
    open('Overall_Metrics_github.h5', 'wb').write(r.content)
    overallMetrics = pd.read_hdf('Overall_Metrics_github.h5', 'overallMetrics')

    r = requests.get(rankingDictFile)
    rankingDict = r.json()
    # print(len(rankingDict))

    resultsFull = pd.read_csv(compositeResultsFile)
    resultsFull['Date'] = pd.to_datetime(resultsFull['Date'])

    results = pd.read_csv(rankingResultsFile)
    results['Date'] = pd.to_datetime(results['Date'])

    return overallMetrics, rankingDict, resultsFull, results


# Import data from Guthub
overallMetrics, rankingDict, resultsFull, results = import_from_github()
# print(list(results))

# Team list
rankingDf = pd.DataFrame.from_dict(rankingDict, orient='index')
rankingDfFilter = rankingDf.loc[
    # ((rankingDf['yearCount'] > 50) and (rankingDf['gameCount'] > 25)) |
    ((rankingDf['gameCount'] / rankingDf['yearCount']) > 5)]
teamList = list(rankingDfFilter.index.values)

currentBestTeams = rankingDfFilter.nlargest(10, rankMethod)
currentBestTeams = list(currentBestTeams.index.values)
# print(currentBest)

# %% Create Dashboard
st.title('College Hockey Rankings')
st.header('by @sckilcoyne with data from CHN')

# Interface
plotTeams = st.sidebar.multiselect('Teams', teamList, currentBestTeams)

currentSeason = max(resultsFull.Season)
plotYears = st.sidebar.slider('Seasons',
                              min(resultsFull.Season),
                              currentSeason,
                              (currentSeason-5, currentSeason))
seasonCount = plotYears[1] - plotYears[0] + 1
seasonRange = range(plotYears[0], plotYears[1] + 1)

comparisonData = st.sidebar.checkbox('Season Extremes', True)

# Plots
legend = []
fig, axs = plt.subplots(1, seasonCount, squeeze=False, sharey=True)
fig.subplots_adjust(wspace=0.05)  # adjust space between axes

# Make each ranking system use same color but allow intra-season gaps
cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
custom_lines = []

for i, ax in enumerate(axs.flat):  # Subplot for each season
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(left=False)
    ax.xaxis.set_major_locator(mdates.YearLocator())

    seasonYear = seasonRange[i]

    # Add overall metrics for season
    if comparisonData:
        allGamesSeason = resultsFull.loc[resultsFull['Season'] == seasonYear]
        seasonStart = allGamesSeason.Date.min()
        seasonEnd = allGamesSeason.Date.max()
        seasonMax = overallMetrics.loc[(
            seasonYear, 'Average'), (rankMethod, 'seasonMax')]
        seasonMin = overallMetrics.loc[(
            seasonYear, 'Average'), (rankMethod, 'seasonMin')]
        seasonMean = overallMetrics.loc[(
            seasonYear, 'Average'), (rankMethod, 'seasonMean')]
        ax.hlines(seasonMax, seasonStart, seasonEnd,
                  color='gray', linestyles='dotted')
        ax.hlines(seasonMin, seasonStart, seasonEnd,
                  color='gray', linestyles='dotted')
        ax.hlines(seasonMean, seasonStart, seasonEnd,
                  color='gray', linestyles='dotted')

    for team in plotTeams:
        teamGames = rk.team_games(results, team)

        seasonGames = teamGames.groupby('Season')
        seasonGames = teamGames.loc[teamGames.Season == seasonYear]
        ax.plot(seasonGames[rankMethod])

ax.legend(plotTeams)  # , bbox_to_anchor=(1.5, 0.5))

fig.set_figheight(12)
fig.set_figwidth(15)
fig.suptitle('Team Elo over Time')
st.pyplot(fig)

# Dataframe
st.dataframe(rankingDfFilter)

test = 30
# Info
st.markdown('_Elo rating system:_')
st.latex(r''' R'_{Home} = R_{Home} + K (S_{Home} - E_{Home})''')
st.latex(r''' E_{Home} = \frac{Q_A}{Q_A+Q_B}''')
st.latex(
    r''' Q_{Home} = 10^\frac{R_{Home}+{HF}+{HI}}{400}''')
st.latex(r''' Q_{Away} = 10^\frac{R_{Away}}{400}''')
st.latex(f''' K = {test}''')
st.latex(f''' HF (Home Field Advantage) = {test}''')
st.latex(f''' HI (Home Ice Advantage) = {test}''')

# =============================================================================
# Qa = pow(10, (homeElo + hfAdv + hiAdv) / 400)
# Qb = pow(10, awayElo / 400)
# Ea = Qa / (Qa + Qb)
# =============================================================================
