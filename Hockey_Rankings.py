# -*- coding: utf-8 -*-
"""
Setup workspace.

@author: Scott
"""

# Setup

import Rankings as rk
import Rankings_Optimize as rkopt
import Ranking_Plots as rkplt

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

    print(results.shape)
    print(resultsShrink.shape)
    return resultsShrink


# Initiailize for All Ranking Types
ratingCoeff = {}
ratingCoeff['simpleElo'] = {'initRating': 1500,
                            'avgRating': 1500,
                            'kRating': 30,
                            'regress': 0,
                            'hfAdvantage': 0,
                            'goalDiffExp': 0}

ratingCoeff['basicElo'] = {'initRating': 1300,
                           'avgRating': 1500,
                           'kRating': 30,
                           'regress': 0.3,
                           'hfAdvantage': 0,
                           'goalDiffExp': 0}

ratingCoeff['hfAdvElo'] = {'initRating': 1300,
                           'avgRating': 1500,
                           'kRating': 30,
                           'regress': 0.3,
                           'hfAdvantage': 30,
                           'goalDiffExp': 0}

ratingCoeff['fullElo'] = {'initRating': 1300,
                          'avgRating': 1500,
                          'kRating': 30,
                          'regress': 0.3,
                          'hfAdvantage': 30,
                          'goalDiffExp': 0.2}

# print(list(ratingCoeff.keys()))

for rankingType in list(ratingCoeff.keys()):
    results[rankingType + ' Away'] = np.nan
    results[rankingType + ' Home'] = np.nan
    results[rankingType + ' Error'] = np.nan

# Run single rankings
# rankingType = 'simpleElo'
rankingType = ['basicElo']

results, rankingDict = rk.game_ranking(results, ratingCoeff, rankingType)

# print(resultsShrink.iterrows())

# for row in resultsShrink.itertuples(index=False):
# for index, row in enumerate(resultsShrink.itertuples(index=False)):
# #     season = resultsShrink.Season[row]
# #     print('Index: ' + str(row) + '  Season: ' + str(season))
#     print('Index: ' + str(index))

# optimizeElo(resultsShrink, ratingCoeff, rankingType)
