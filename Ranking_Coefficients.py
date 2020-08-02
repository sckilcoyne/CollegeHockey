# -*- coding: utf-8 -*-
"""
Generate Ranking System Coefficients.

Created on Sun Jul 19 11:31:12 2020

@author: Scott
"""


def coefficients(debug=False):
    """
    Generate Ranking System Coefficients.

    Parameters
    ----------
    debug : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    ratingCoeff : TYPE
        DESCRIPTION.

    """
    # Initiailize for All Ranking Types
    ratingCoeff = {}
    ratingCoeff['simpleElo'] = {'initRating': 1500,
                                'avgRating': 1500,
                                'kRating': 30,
                                'regress': 0,
                                'hfAdvantage': 0,
                                'hiAdvantage': 0,
                                'goalDiffExp': 0}

    ratingCoeff['basicElo'] = {'initRating': 1300,
                               'avgRating': 1500,
                               'kRating': 30,
                               'regress': 0.3,
                               'hfAdvantage': 0,
                               'hiAdvantage': 0,
                               'goalDiffExp': 0}

    ratingCoeff['hfAdvElo'] = {'initRating': 1300,
                               'avgRating': 1500,
                               'kRating': 30,
                               'regress': 0.3,
                               'hfAdvantage': 30,
                               'hiAdvantage': 0,
                               'goalDiffExp': 0}

    ratingCoeff['fullElo'] = {'initRating': 1300,
                              'avgRating': 1500,
                              'kRating': 30,
                              'regress': 0.3,
                              'hfAdvantage': 10,
                              'hiAdvantage': 20,
                              'goalDiffExp': 0.2}

    if debug:
        print(list(ratingCoeff.keys()))

    return ratingCoeff
