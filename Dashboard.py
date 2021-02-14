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

# Import custom modules
import rankings as rk
import Ranking_Plots as rkplt
import Ranking_Coefficients
import Import_Results as ir

debug = [False, True, 'verbose']

# %% Set up data
# Import Data
# =============================================================================
# resultsFile = 'https://raw.githubusercontent.com/sckilcoyne/CollegeHockey/master/Results_Composite.csv'
#
# resultsLoaded = ir.load_composite_results(resultsFile)
# resultsFull = resultsLoaded.copy()
#
# # Get ranking coefficients
# ratingCoeff = Ranking_Coefficients.coefficients()
#
# # Ranking Models to run
# rankingType = ['simpleElo']
#
# # Team list
# teamList = rk.find_teams(resultsFull)
#
# # Run ranking models
# results, rankingDict = rk.game_ranking(resultsFull, ratingCoeff,
#                                        rankingType, debug[0])
#
# # Generate Summary Statistics
# rankingDict = rk.team_season_metrics(results, rankingDict)
# overallMetrics = rk.overall_metrics(rankingDict)
# =============================================================================


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
    print(len(rankingDict))

    resultsFull = pd.read_csv(compositeResultsFile)

    results = pd.read_csv(rankingResultsFile)

    return overallMetrics, rankingDict, resultsFull, results


# Import data from Guthub
overallMetrics, rankingDict, resultsFull, results = import_from_github()
print(list(results))

# Team list
teamList = rk.find_teams(resultsFull)

# %% Create Dashboard
st.title('College Hockey Rankings')
st.header('by @sckilcoyne with data from CHN')

plotTeams = st.sidebar.multiselect('Teams', teamList)

legend = []
fig, ax = plt.subplots()
for team in plotTeams:

    teamGames = rk.team_games(results, team)

    # Get list of ranking types
    rankMethod = list(teamGames)
    del rankMethod[0]  # Remove Season column
    rankMethod = rankMethod[0]

    ax.plot(teamGames['simpleElo'])

    legend = legend + [team]

ax.legend(legend)
st.pyplot(fig)
