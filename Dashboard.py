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
import Ranking_Coefficients as rc
import Import_Results as ir

debug = [False, True, 'verbose']

# rankMethod = 'fullElo'

# %% Set plot style
# matplotlib.rcParams.update(matplotlib.rcParamsDefault)
githubContent = 'https://raw.githubusercontent.com/sckilcoyne/CollegeHockey/'
githubBranch = 'master'
styleFile = 'fig_style'
styleFile = githubContent + githubBranch + '/' + styleFile + '.mplstyle'
plt.style.use(styleFile)

# %% Create Dashboard
st.set_page_config(page_title='College Hockey Ranking',
                   page_icon=':ice_hockey_stick_and_puck:',
                   initial_sidebar_state='expanded',
                   layout='wide')


st.title('College Hockey Rankings')
'''
by [@sckilcoyne](https://github.com/sckilcoyne/CollegeHockey)
with data from [CHN](https://www.collegehockeynews.com/)
'''

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
coeff = rc.coefficients()

# Team list
rankingDf = pd.DataFrame.from_dict(rankingDict, orient='index')
rankingDfFilter = rankingDf.loc[
    # ((rankingDf['yearCount'] > 50) and (rankingDf['gameCount'] > 25)) |
    ((rankingDf['gameCount'] / rankingDf['yearCount']) > 5)]
teamList = list(rankingDfFilter.index.values)


# %% Sidebar Interface
container = st.sidebar.beta_container()


currentSeason = max(resultsFull.Season)
plotYears = st.sidebar.slider(
    'Seasons',
    min(resultsFull.Season),
    currentSeason,
    (currentSeason-5, currentSeason),
    help='Range of seasons to plot ratings over.')
seasonCount = plotYears[1] - plotYears[0] + 1
seasonRange = range(plotYears[0], plotYears[1] + 1)

helpNote = 'Adds the Max, Min and Median rating of all teams for each season' \
    ' to the rating plot.'
comparisonData = st.sidebar.checkbox(
    'Season Extremes', True,
    help=helpNote)

rankMethods = rankingDfFilter.columns[2:]
rankDefault = rankMethods.to_list().index('fullElo')
rankMethod = st.sidebar.selectbox(
    'Ranking Method', rankMethods, index=rankDefault,
    help='Choose which rating method to display.')

helpNote = 'Select teams to compare ratings over time.' \
    'Defaults to current highest rated teams.'
currentBestTeams = rankingDfFilter.nlargest(5, rankMethod)
currentBestTeams = list(currentBestTeams.index.values)
plotTeams = container.multiselect(
    'Teams', teamList, currentBestTeams,
    help=helpNote)

# %% Team Comparison Plot
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
fig.suptitle('Team Ratings Comparison using ' + rankMethod,
             fontsize='x-large',
             fontweight='heavy')
plt.tight_layout()
st.pyplot(fig)

# %% Current Ratings Dataframe
with st.beta_expander('Current Rating of All Teams'):
    dfDisplay = rankingDfFilter[['gameCount', 'yearCount', rankMethod]].copy()
    dfDisplay.sort_values(rankMethod, ascending=False, inplace=True)
    dfDisplay = dfDisplay.astype(int)
    st.dataframe(dfDisplay)

# %% Background of rating system selected
with st.beta_expander('Rating Method (' + rankMethod +
                      ') Background and Parameters'):

    # Variables Used
    kRating = coeff[rankMethod]['kRating']
    hfa = coeff[rankMethod]['hfAdvantage']
    hia = coeff[rankMethod]['hiAdvantage']
    regress = coeff[rankMethod]['regress']

    col1, col2 = st.beta_columns(2)

    # Formulas
    with col1:
        st.markdown('_Elo rating system:_')
        st.latex(r''' R'_{Home} = R_{Home} + K (S_{Home} - E_{Home})''')
        st.latex(r''' E_{Home} = \frac{Q_A}{Q_A+Q_B}''')
        st.latex(
            r''' Q_{Home} = 10^\frac{R_{Home}+{HF}+{HI}}{400}''')
        st.latex(r''' Q_{Away} = 10^\frac{R_{Away}}{400}''')

    # parameters
    with col2:
        st.markdown('_' + rankMethod + ' parameters:_')
        st.latex(f''' K = {kRating}''')
        st.latex(f''' HF (Home Field Advantage) = {hfa}''')
        st.latex(f''' HI (Home Ice Advantage) = {hia}''')
        st.latex(f''' Season Regression = {regress}''')

# %% Rating system comparisions
with st.beta_expander('Rating System Comparisons'):
    '''
    # WIP
    '''

# %% Other sections/dashboards to be added
# Conference comparisons/average ratings
#   With different methods of conference ratings (top, top quartile, mean,
#       median, top 3/x, etc.)

# Future game predicitions
# End of season predicitons
#   Make tourny, win title, etc.

# Detailed history of individual teams
#   Call out highs and lows
#   Season-by-season box plot
#   Biggest upset (both ways)

# Comparison to polls
