# -*- coding: utf-8 -*-
"""
Functions to calculate optimal parameters for ranking systems.

@author: Scott
"""

import Rankings as rk
import Import_Results as ir
import Ranking_Coefficients

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
# from importlib import reload
# reload(rk)

# Import Data
resultsFull = pd.read_csv('Results_Composite.csv')
print('Results shape: ', resultsFull.shape)
results = ir.results_shrink(resultsFull.copy(), 2000, 2019)

def ranking_error(values, rankType):
    global results
    ratingCoeff = {}
    ratingCoeff[rankType] = {'initRating': values[1],
                             'avgRating': 1500,
                             'kRating': values[0],
                             'regress': values[2],
                             'hfAdvantage': 0,
                             'hiAdvantage': 0,
                             'goalDiffExp': 0}
    
    # Run ranking with given coefficients
    results, rankingDict = rk.game_ranking(results, ratingCoeff, [rankType],
                                           False, False)
    
    # Get average error of all results
    errorCol = rankType + '_Error'
    # errorMedian = results[errorCol].median()
    errorMean = results[errorCol].mean()
    
    return errorMean
        
        
def optimize_elo(ratingCoeff, rankType):
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
    x0  = np.array([30, 1300, 0.3])
    res = opt.minimize(ranking_error, x0, args=(rankType), method='nelder-mead')
    
    print(res)
    return res


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

# Setup
ratingCoeff = Ranking_Coefficients.coefficients()
rankingType = ['optimizeElo']


# Run Optimization
optimize_elo(ratingCoeff, rankingType[0])