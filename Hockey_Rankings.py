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
import Rankings_Optimize as rkopt
import Ranking_Plots as rkplt
import Ranking_Coefficients

import pandas as pd
import numpy as np
# %matplotlib widget
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# import matplotlib.cbook as cbook
# from pandas.plotting import register_matplotlib_converters
# register_matplotlib_converters()


# =============================================================================
# %matplotlib inline
# # %matplotlib notebook
# %matplotlib widget
# =============================================================================

# Import Data
results = pd.read_csv('Results_Composite.csv')
print('Results shape: ', results.shape)


def results_shrink(results, startYear=2010, endYear=2019):
    """
    Select a subsection of all results.

    Parameters
    ----------
    results : TYPE
        DESCRIPTION.
    startYear : TYPE, optional
        Season start of selection. The default is 2010.
    endYear : TYPE, optional
        Season start of end of selection. The default is 2019.

    Returns
    -------
    resultsShrink : TYPE
        Subsection of results.

    """
    resultsShrink = results[results.Season >= startYear]

    print('Results limited to ', str(startYear), ' through ', str(endYear))
    print('Results shape: ', resultsShrink.shape)
    return resultsShrink


ratingCoeff = Ranking_Coefficients.coefficients()

# for rankingType in list(ratingCoeff.keys()):
#     results[rankingType + ' Away'] = np.nan
#     results[rankingType + ' Home'] = np.nan
#     results[rankingType + ' Error'] = np.nan

# Run single rankings
rankingType = ['simpleElo']
# rankingType = ['basicElo']

results = results_shrink(results)

for rankType in rankingType:
    results[rankType + ' Away'] = np.nan
    results[rankType + ' Home'] = np.nan
    results[rankType + ' Error'] = np.nan

results, rankingDict = rk.game_ranking(results, ratingCoeff, rankingType)


# %% Optimization

resultsShrink = results_shrink(results)

rkopt.optimizeElo(resultsShrink, ratingCoeff, rankingType)
