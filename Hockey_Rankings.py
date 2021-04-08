# -*- coding: utf-8 -*-
"""
Setup workspace.

Sources:
    https://en.wikipedia.org/wiki/Elo_rating_system#Mathematical_details
    http://hockeyanalytics.com/2016/07/elo-ratings-for-the-nhl/

    http://www.eloratings.net/system.html
    https://en.wikipedia.org/wiki/Elo_rating_system
    https://www.reddit.com/r/hockey/comments/21oo9d/presenting_the_world_hockey_elo_ratings/
    http://implyingrigged.info/wiki/Elo_Ratings
    http://clubelo.com/Articles/RatingSystem.html
    http://lastplanetranking.blogspot.com/2013/11/about.html
    http://www.baseballprospectus.com/article.php?articleid=5247
    http://fivethirtyeight.com/features/how-we-calculate-nba-elo-ratings/
    http://fivethirtyeight.com/datalab/introducing-nfl-elo-ratings/


@author: Scott
"""

# %% Setup
# Import common modules
import pandas as pd
import importlib
import matplotlib.pyplot as plt

# Import all custom modules
import utils.Rankings as rk
import utils.Ranking_Plots as rkplt
from utils.Ranking_Coefficients import coefficients
import utils.Import_Results as ir

debug = [False, True, 'verbose']

# %% Run initial stuff
# Import Data
# resultsFull = pd.read_csv('Results_Composite.csv')
resultsFull = ir.load_composite_results('local')

# Get ranking coefficients
ratingCoeff = coefficients()

# Ranking Models to run
rankingType = ['simpleElo']
# rankingType = ['basicElo']
rankingType = ['simpleElo', 'basicElo', 'hfAdvElo', 'fullElo']

# Shrink results scope for development speed
# results = ir.results_shrink(resultsFull.copy(), 2010, 2015)
results = resultsFull

# Run ranking models
results, rankingDict = rk.game_ranking(results, ratingCoeff,
                                       rankingType, debug[0])

# Generate Summary Statistics
rankingDict = rk.team_season_metrics(results, rankingDict)
overallMetrics = rk.overall_metrics(rankingDict)


# %%-----Development Stuff
# Prep plots
teamGames = rk.team_games(results)


# %% Ploting
