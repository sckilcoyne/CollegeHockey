# -*- coding: utf-8 -*-
"""
Functions to calculate rankings.

@author: Scott
"""

# Setup
import pandas as pd
import numpy as np


# Find all teams in database
def find_teams(results):
    """
    todo.

    Parameters
    ----------
    results : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    allTeams = pd.Series(results['Home']).unique()
    allTeams = np.append(allTeams, pd.Series(results['Away']).unique())
    allTeams = np.unique(allTeams)

    # print(allTeams)
    return(allTeams)


# Initialize rankings for all teams
def rankings_init(allTeams, ratingCoeff, rankingType):
    """
    todo.

    Parameters
    ----------
    allTeams : TYPE
        DESCRIPTION.
    ratingCoeff : TYPE
        DESCRIPTION.
    rankingType : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    rankingDict = {}

    for x, value in np.ndenumerate(allTeams):
        # print(value)
        rankingDict[value] = {
            rankingType: ratingCoeff[rankingType]['initRating']}
        # print(x)

    # print(rankingDict)
    return(rankingDict)


# Ranking Formulas
# Simple Elo: no HF, no GD
def elo_simple(homeElo, awayElo, goalDiff, k):
    """
    todo.

    Parameters
    ----------
    homeElo : TYPE
        DESCRIPTION.
    awayElo : TYPE
        DESCRIPTION.
    goalDiff : TYPE
        DESCRIPTION.
    k : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    if goalDiff > 0:
        result = 1
    elif goalDiff < 0:
        result = 0
    else:
        result = 0.5

    Qa = pow(10, homeElo/400)
    Qb = pow(10, awayElo/400)
    Ea = Qa / (Qa + Qb)
#     Eb = Qb / (Qa + Qb)

    deltaElo = round(k * (result - Ea), 2)
    predictError = (result - Ea) ** 2

    homeElo_adj = round(homeElo + deltaElo, 2)
    awayElo_adj = round(awayElo - deltaElo, 2)

#     print('Qa: ', Qa, ' Qb: ', Qb, ' Ea: ', Ea, ' Eb: ', Eb, ' homeElo_adj: ', homeElo_adj, ' awayElo_adj: ',awayElo_adj)

    return (homeElo_adj, awayElo_adj, predictError)


def rating_elo(homeElo, awayElo, goalDiff, ratingCoeffMethod):
    """
    todo.

    Parameters
    ----------
    homeElo : TYPE
        DESCRIPTION.
    awayElo : TYPE
        DESCRIPTION.
    goalDiff : TYPE
        DESCRIPTION.
    ratingCoeffMethod : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    k = ratingCoeffMethod['kRating']
    hfAdv = ratingCoeffMethod['hfAdvantage']

    if goalDiff > 0:
        result = 1
    elif goalDiff < 0:
        result = 0
    else:
        result = 0.5

    Qa = pow(10, (homeElo + hfAdv)/400)
    Qb = pow(10, awayElo/400)
    Ea = Qa / (Qa + Qb)
#     Eb = Qb / (Qa + Qb)

    deltaElo = round(k * (result - Ea), 2)
    predictError = (result - Ea) ** 2

    homeElo_adj = round(homeElo + deltaElo, 2)
    awayElo_adj = round(awayElo - deltaElo, 2)

#     print('Qa: ', Qa, ' Qb: ', Qb, ' Ea: ', Ea, ' Eb: ', Eb, ' homeElo_adj: ', homeElo_adj, ' awayElo_adj: ',awayElo_adj)

    return (homeElo_adj, awayElo_adj, predictError)


# Regress Rankings at Season Start
def season_start(results, rankingDict, ratingCoeff, rankingType, season,
                 allTeams):
    """
    todo.

    Parameters
    ----------
    results : TYPE
        DESCRIPTION.
    rankingDict : TYPE
        DESCRIPTION.
    ratingCoeff : TYPE
        DESCRIPTION.
    rankingType : TYPE
        DESCRIPTION.
    season : TYPE
        DESCRIPTION.
    allTeams : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    seasonGames = results[results.Season == season]

    seasonTeams = pd.concat([seasonGames['Home'], seasonGames['Away']]).unique()

    # print(seasonGames)
#     print(seasonTeams)

    regress = ratingCoeff[rankingType]['regress']
    avgRating = ratingCoeff[rankingType]['avgRating']

    for team in allTeams:
        # if play this season and last, regress
        if team in seasonTeams:
            currentRating = rankingDict[team][rankingType]
            rankingDict[team][rankingType] = round(currentRating - (regress * (currentRating - avgRating)), 2)
    #         print(team + " played in " + str(season) + '. Regressed from ' + str(currentRating) + ' to ' + str(rankingDict[team][rankingType]))

        # if don't play this season, reset
        else:
            rankingDict[team][rankingType] = ratingCoeff[rankingType]['initRating']
    #         print(team + " reverted to " + str(ratingCoeff[rankingType]['initRating']))

    return(rankingDict)


# Calculate rankings for each match
def game_ranking(results, ratingCoeff, rankingType):
    """
    todo.

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
    allTeams = find_teams(results)

    for index, row in enumerate(results.itertuples(index=False)):
        # print(row)
        # season = results.Season[index]
        season = row.Season
#         print('Index: ' + str(index) + '  Season: ' + str(season))
        for rankingMethod in rankingType:
            if index == 0:
                rankingDict = rankings_init(allTeams, ratingCoeff,
                                            rankingMethod)
                seasonLast = season
                print('Start ranking ' + str(season))
    #         elif (results[index].season - results[index - 1].season) > 0:
#             elif (results.Season[index] - results.Season[index - 1]) > 0:
            elif (season - seasonLast) > 0:
                rankingDict = season_start(results, rankingDict, ratingCoeff,
                                           rankingMethod, season, allTeams)
                seasonLast = season
    #             print(str(season))

            teamAway = row.Away
            teamHome = row.Home

            eloAway = rankingDict.get(teamAway, {}).get(rankingMethod)
            eloHome = rankingDict.get(teamHome, {}).get(rankingMethod)

#             goalDiff = row['Home Score'] - row['Away Score']
            goalDiff = row[5] - row[2]

            if 'Elo' in rankingMethod:
                [eloHome, eloAway, predictError] = rating_elo(eloHome, eloAway,
                                                              goalDiff,
                                                              ratingCoeff[rankingMethod])
            else:
                raise ValueError('Unknown Ranking Method.')

#         [eloHome, eloAway, predictError] = elo_simple(eloHome, eloAway, goalDiff, ratingCoeff[rankingType]['kRating'])

            # Update Current Elo Tracker
            rankingDict[teamAway][rankingMethod] = eloAway
            rankingDict[teamHome][rankingMethod] = eloHome

            # Add Updated Elo to Results table
            results.loc[index, rankingMethod + ' Away'] = eloAway
            results.loc[index, rankingMethod + ' Home'] = eloHome
            results.loc[index, rankingMethod + ' Error'] = predictError

        # print(teamAway,', ', teamHome)
        # print(rankingDict[teamAway]['Elo_Simple'],', ',rankingDict[teamHome]['Elo_Simple'])

    # Write to CSV
    results.to_csv(path_or_buf='Results_Rankings.csv', index='False')

    return (results, rankingDict)
