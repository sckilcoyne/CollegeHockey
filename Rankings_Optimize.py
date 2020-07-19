# -*- coding: utf-8 -*-
"""
Functions to calculate optimal parameters for ranking systems.

@author: Scott
"""

import ranking as rk
from scipy.optimize import minimize
# from importlib import reload
# reload(rk)


def optimizeElo(results, ratingCoeff, rankingType):
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
