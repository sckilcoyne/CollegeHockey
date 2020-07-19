# -*- coding: utf-8 -*-
"""
Functions to calculate optimal parameters for ranking systems.

@author: Scott
"""

import Rankings as rk

import pandas as pd
# import numpy as np
import matplotlib.pyplot as plt
# from scipy.optimize import minimize
# from importlib import reload
# reload(rk)


def optimize_elo(results, ratingCoeff, rankingType):
    """
    Calculate optimal parameters for Elo ranking.

    Parameters
    ----------
    results : TYPE
        DESCRIPTION.
    ratingCoeff : TYPE
        DESCRIPTION.
    rankingType : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
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


def k_finder(results):
    """
    Find best k value.

    Parameters
    ----------
    results : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    # Iterate rankings through K values
    allTeams = rk.findTeams(results)
    rankingDict = rk.rankingsInit(allTeams, rk.initEloSimple)
    eloError = pd.DataFrame(columns=['k', 'Elo_Error'])

    for k in range(10, 60, 10):
        results, rankingDict = rk.gameRanking(results, rankingDict, k)
    #     print(k)
        averageError = results['simpleElo Error'].mean()
    #     print(averageError)
        eloError = eloError.append({'k': k, 'Elo_Error': averageError},
                                   ignore_index=True)

    eloError.plot(x='k', y='Elo_Error')

    minErroridx = eloError['Elo_Error'].idxmin()
    minError = eloError['Elo_Error'][minErroridx]
    minErrork = eloError['k'][minErroridx]
    plt.plot(minErrork, minError, 'o')
    plt.annotate('Min Error: ' + str(minErrork),
                 xy=(minErrork, minError),
                 xytext=(minErrork, minError + 0.01))

    plt.show()
