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
    debug : bool, optional
        What level of debugging/prints to do. The default is False.

    Returns
    -------
    ratingCoeff : dict
        DESCRIPTION.

    """
    # Initiailize for All Ranking Types
    ratingCoeff = {}
    ratingCoeff['simpleElo'] = {'initRating': 1500,
                                'avgRating': 1500,
                                'kRating': 25,
                                'regress': 0,
                                'hfAdvantage': 0,
                                'hiAdvantage': 0,
                                'goalDiffExp': 0}

    ratingCoeff['basicElo'] = {'initRating': 1150,
                               'avgRating': 1500,
                               'kRating': 25,
                               'regress': 0.1,
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


if __name__ == '__main__':
    # When run as script, create dict in workspace
    ratingCoeff = coefficients()
