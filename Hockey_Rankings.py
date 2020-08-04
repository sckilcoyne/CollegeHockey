# -*- coding: utf-8 -*-
"""
Setup workspace.

Sources:
    https://en.wikipedia.org/wiki/Elo_rating_system#Mathematical_details
    http://hockeyanalytics.com/2016/07/elo-ratings-for-the-nhl/


@author: Scott
"""

# Setup

import Rankings as rk
# import Ranking_Plots as rkplt
import Ranking_Coefficients
import Import_Results as ir

import pandas as pd


# Import Data
resultsFull = pd.read_csv('Results_Composite.csv')
print('Results shape: ', resultsFull.shape)

# results = resultsFull


ratingCoeff = Ranking_Coefficients.coefficients()


# Run single rankings
rankingType = ['simpleElo']
# rankingType = ['basicElo']

results = ir.results_shrink(resultsFull.copy(), 2010, 2010)


debug = [False, True, 'verbose']

results, rankingDict = rk.game_ranking(results, ratingCoeff,
                                       rankingType, debug[0])
