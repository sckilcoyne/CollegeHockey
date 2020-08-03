# -*- coding: utf-8 -*-
"""
Functions to calculate optimal parameters for ranking systems.

@author: Scott
"""

import Rankings as rk
import Import_Results as ir
import Ranking_Coefficients

import pandas as pd
# import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize
# from importlib import reload
# reload(rk)


def ranking_error(results, ratingCoeff, rankType):
    # Run ranking with given coefficients
    results, rankingDict = rk.game_ranking(results, ratingCoeff, rankType)
    
    # Get average error of all results
    errorCol = rankType + '_Error'
    # errorMedian = results[errorCol].median()
    errorMean = results[errorCol].mean()
    
    return errorMean
        
        
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
    optimize.basinhopping(ranking_error


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

# %% Optimization

# Import Data
resultsFull = pd.read_csv('Results_Composite.csv')
print('Results shape: ', resultsFull.shape)

# Setup
ratingCoeff = Ranking_Coefficients.coefficients()
rankingType = ['simpleElo']
results = ir.results_shrink(resultsFull.copy(), 2010, 2011)

# Run Optimization
optimize_elo(results, ratingCoeff, rankingType)