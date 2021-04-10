# -*- coding: utf-8 -*-
"""
Functions to calculate rankings.

@author: Scott
"""

# %% Setup
import pandas as pd
import numpy as np
import json

# %% Functions


def find_teams(results, debug=False):
    """
    Create a list of all teams in results database.

    Parameters
    ----------
    results : TYPE
        Game results database.

    Returns
    -------
    allTeams : numpy list
        List of unique teams in database.

    """
    if debug:
        print('find_teams in Debug mode.')

    allTeams = pd.Series(results['Home']).unique()
    if debug:
        print('Home teams: ' + len(allTeams))

    allTeams = np.append(allTeams, pd.Series(results['Away']).unique())
    if debug:
        print('Home and Away teams: ' + len(allTeams))

    allTeams = np.unique(allTeams)
    if debug:
        print('Unique teams: ' + len(allTeams))

    # print(allTeams)
    print(str(len(allTeams)) + ' unique teams.')

    return allTeams


def rankings_init(allTeams, ratingCoeff, rankingTypes, debug=False):
    """
    Initialize rankings for all teams.

    Parameters
    ----------
    allTeams : numpy list
        List of unique teams in database.
    ratingCoeff : dict
        Dict of parameters for each possible ranking system.
    rankingType : list
        List of which ranking systems to initialize for.

    Returns
    -------
    rankingDict : dict
        Each team and their current ranking for each ranking system.

    """
    if debug:
        print('rankings_init in Debug mode.')
        # print(rankingType)

    rankingDict = {}

    for x, team in np.ndenumerate(allTeams):
        if debug == 'verbose':
            print('x: ' + str(x))
            print('value: ' + str(team))

        rankingDict[team] = {'gameCount': 0, 'yearCount': 1}

        for rankingType in rankingTypes:
            rankingDict[team].update({
                rankingType: ratingCoeff[rankingType]['avgRating']})

    if debug:
        print('rankingDict shape: ' + str(len(rankingDict)))

    if debug == 'verbose':
        print(rankingDict)

    return(rankingDict)


def season_start(results, rankingDict, ratingCoeff, rankingTypes, season,
                 allTeams, debug=False):
    """
    Regress Rankings at Season Start.

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
    rankingDict : TYPE
        DESCRIPTION.

    """
    if debug:
        print('season_start in debug mode.')

    seasonGames = results[results.Season == season]

    seasonTeams = pd.concat(
        [seasonGames['Home'], seasonGames['Away']]).unique()

    if debug == 'verbose':
        print(seasonGames)
        print(seasonTeams)

    # Regress each team's rating
    for team in allTeams:
        if team in seasonTeams:
            yearCount = rankingDict[team]['yearCount']
            rankingDict[team]['yearCount'] = yearCount + 1

        for rankingType in rankingTypes:
            regress = ratingCoeff[rankingType]['regress']
            avgRating = ratingCoeff[rankingType]['avgRating']

            # if play this season and last, regress
            if team in seasonTeams:
                currentRating = rankingDict[team][rankingType]
                rankingDict[team][rankingType] = round(
                    currentRating - (regress * (currentRating - avgRating)), 2)
                if debug:
                    print(team + ' played in ' + str(season) +
                          '. Regressed from ' + str(currentRating) +
                          ' to ' + str(rankingDict[team][rankingType]))

            # if don't play this season, reset
            else:
                initRating = ratingCoeff[rankingType]['initRating']
                rankingDict[team][rankingType] = initRating
                if debug:
                    print(team + " reverted to " +
                          str(ratingCoeff[rankingType]['initRating']))

    return(rankingDict)


# %% Ranking Formulas
def elo_simple(homeElo, awayElo, goalDiff, k, debug=False):
    """
    Elo ranking system based only on wins.

    No Homefield Advantage.
    No Goal Diferential.
    No season regression.

    Parameters
    ----------
    homeElo : float
        Elo Rating of home team.
    awayElo : float
        Elo Rating of away team.
    goalDiff : Int
        Goal difference of game (Home - Away)
    k : Int
        Elo k-factor.

    Returns
    -------
    homeElo_adj : float
        Adjustment to home team's elo
    awayElo_adj : float
        Adjustment to away team's elo
    predictError : float
        Prediction error as a Brier score for event

    """
    if debug:
        print('elo_simple in debug mode')

    # Determine winner of game
    if goalDiff > 0:
        result = 1
    elif goalDiff < 0:
        result = 0
    else:
        result = 0.5

    # Calutlate expected match score
    Qa = pow(10, homeElo / 400)
    Qb = pow(10, awayElo / 400)
    Ea = Qa / (Qa + Qb)
    Eb = Qb / (Qa + Qb)

    # Change in Elo ratings
    deltaElo = round(k * (result - Ea), 2)

    # Expected match score error
    predictError = (result - Ea) ** 2

    # Adjust Elo ratings of each team based on result
    homeElo_adj = round(homeElo + deltaElo, 2)
    awayElo_adj = round(awayElo - deltaElo, 2)

    if debug:
        print('Qa: ', Qa,
              ' Qb: ', Qb,
              ' Ea: ', Ea,
              ' Eb: ', Eb,
              ' homeElo_adj: ', homeElo_adj,
              ' awayElo_adj: ', awayElo_adj)

    return (homeElo_adj, awayElo_adj, predictError)


def rating_elo(homeElo, awayElo, goalDiff, ratingCoeffMethod, debug=False):
    """
    Elo ranking system.

    Includes Homefield Advantage.

    Parameters
    ----------
    homeElo : float
        Elo Rating of home team.
    awayElo : float
        Elo Rating of away team.
    goalDiff : Int
        Goal difference of game (Home - Away)
    ratingCoeffMethod : TYPE
        DESCRIPTION

    Returns
    -------
    homeElo_adj : float
        Adjustment to home team's elo
    awayElo_adj : float
        Adjustment to away team's elo
    predictError : float
        Prediction error as a Brier score for event


    """
    if debug:
        print('rating_elo in debug mode.')
        print(ratingCoeffMethod)

    k = ratingCoeffMethod['kRating']
    hfAdv = ratingCoeffMethod['hfAdvantage']  # Home Team
    hiAdv = ratingCoeffMethod['hiAdvantage']  # Home Ice
    # goalDiffExp = ratingCoeffMethod['goalDiffExp']

    # Determine winner of game
    if goalDiff > 0:
        result = 1
    elif goalDiff < 0:
        result = 0
    else:
        result = 0.5

    if debug:
        print("home Elo: " + type(homeElo).__name__)
        print("hf Adv: " + type(hfAdv).__name__)
        print("hi Adv: " + type(hiAdv).__name__)

    # Calutlate expected match score
    Qa = pow(10, (homeElo + hfAdv + hiAdv) / 400)
    Qb = pow(10, awayElo / 400)
    Ea = Qa / (Qa + Qb)
    Eb = Qb / (Qa + Qb)

    # Change in Elo ratings
    deltaElo = round(k * (result - Ea), 2)

    # Expected match score error
    predictError = (result - Ea) ** 2

    # Adjust Elo ratings of each team based on result
    homeElo_adj = round(homeElo + deltaElo, 2)
    awayElo_adj = round(awayElo - deltaElo, 2)

    if debug:
        print('Qa: ', Qa,
              ' Qb: ', Qb,
              ' Ea: ', Ea,
              ' Eb: ', Eb,
              ' homeElo_adj: ', homeElo_adj,
              ' awayElo_adj: ', awayElo_adj)

    return (homeElo_adj, awayElo_adj, predictError)


def game_ranking(results, ratingCoeff, rankingType,
                 debug=False, saveResults=True):
    """
    Calculate rankings for each match.

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
    results : TYPE
        DESCRIPTION.
    rankingDict : TYPE
        DESCRIPTION.

    """
    if debug == 'verbose':
        debugVerbose = True
        debug = True
    else:
        debugVerbose = False

    if debug:
        print('game_ranking in debug mode.')
        sep = ", "
        print("Ranking systems to run: " + sep.join(rankingType))

    # Get list of all teams in results
    allTeams = find_teams(results)

    # Create columns for ranking results for each ranking system
    for rankType in rankingType:
        results[rankType + '_Away'] = np.nan
        results[rankType + '_Home'] = np.nan
        results[rankType + '_Error'] = np.nan

    # Evaluate each game for given ranking methods
    print('Start scoring each game')
    for index, row in enumerate(results.itertuples(index=True)):
        season = row.Season

        if debugVerbose:
            print('Index: ' + str(index) + '  Season: ' + str(season))
            print(row)

        # Intitialize first season
        if index == 0:
            rankingDict = rankings_init(allTeams, ratingCoeff,
                                        rankingType)  # , debug)
            seasonLast = season

            if debug:
                print('First season initialized.')

        # Initialize new seasons
        elif (season - seasonLast) > 0:
            rankingDict = season_start(results, rankingDict, ratingCoeff,
                                       rankingType, season, allTeams, debug)
            seasonLast = season

            if debug:
                print(str(season) + ' season initialized')

        for rankingMethod in rankingType:
            if debug:
                print(rankingMethod)
                # print(row)
                # print(ratingCoeff)

            # Home and Away teams
            teamAway = row.Away
            teamHome = row.Home

            # Home and Away teams' ratings
            eloAway = rankingDict.get(teamAway, {}).get(rankingMethod)
            eloHome = rankingDict.get(teamHome, {}).get(rankingMethod)

            goalDiff = row.Home_Score - row.Away_Score
            # goalDiff = row[5] - row[2]

            if debug:
                print("Away: " + teamAway + " Elo: " + str(eloAway))
                print("Home: " + teamHome + " Elo: " + str(eloHome))

            # Choose ranking function based on method
            if 'Elo' in rankingMethod:
                rateCoeff = ratingCoeff[rankingMethod]
                [eloHome, eloAway, predictError] = rating_elo(eloHome,
                                                              eloAway,
                                                              goalDiff,
                                                              rateCoeff)
            else:
                raise ValueError('Unknown Ranking Method.')

        # [eloHome, eloAway, predictError] = elo_simple(
        #     eloHome, eloAway, goalDiff, ratingCoeff[rankingType]['kRating'])

            # Update Current Ranking Tracker
            rankingDict[teamAway][rankingMethod] = eloAway
            rankingDict[teamHome][rankingMethod] = eloHome

            # Add Updated Elo to Results table
            results.at[row.Index, rankingMethod + '_Away'] = eloAway
            results.at[row.Index, rankingMethod + '_Home'] = eloHome
            results.at[row.Index, rankingMethod + '_Error'] = predictError

        # Increment game counter
        awayCount = rankingDict[teamAway]['gameCount'] + 1
        homeCount = rankingDict[teamHome]['gameCount'] + 1
        rankingDict[teamAway]['gameCount'] = awayCount
        rankingDict[teamHome]['gameCount'] = homeCount

    # Write to CSV
    if saveResults:
        path_or_buf = 'Results_Rankings.csv'
        results.to_csv(path_or_buf=path_or_buf, index='False')
        print('Results saved to ' + path_or_buf)

        with open('Ranking_Dict.txt', 'w') as file:
            # use `json.loads` to do the reverse
            file.write(json.dumps(rankingDict))

    return (results, rankingDict)

# %% Results analysis


def team_games(results, team='Northeastern'):
    """
    Collect all games by given team.

    Parameters
    ----------
    results : TYPE
        DESCRIPTION.
    team : TYPE, optional
        DESCRIPTION. The default is 'Northeastern'.

    Returns
    -------
    teamGames : TYPE
        DESCRIPTION.

    """
    # Get columns
    awayCol = ([col for col in results.columns if '_Away' in col])
    homeCol = ([col for col in results.columns if '_Home' in col])
    commonCols = ['Date', 'Season']

    awayGames = results.loc[results['Away'] == team, commonCols + awayCol]
    homeGames = results.loc[results['Home'] == team, commonCols + homeCol]

    awayGames = awayGames.drop_suffix('_Away')
    homeGames = homeGames.drop_suffix('_Home')

    teamGames = awayGames.append(homeGames)

    teamGames['Date'] = pd.to_datetime(teamGames['Date'], format='%Y-%m-%d')
    teamGames = teamGames.sort_values(by='Date')

    teamGames = teamGames.set_index('Date')

    return teamGames


def team_season_metrics(results, rankingDict):
    """
    Add season summary stats for each team to ratingDict.

    Parameters
    ----------
    results : TYPE
        DESCRIPTION.
    rankingDict : TYPE
        DESCRIPTION.

    Returns
    -------
    rankingDict : TYPE
        DESCRIPTION.

    """
    for team in rankingDict:
        teamGames = team_games(results, team)
        groupedGames = teamGames.groupby(['Season'])
        seasonMean = groupedGames.mean()
        seasonMax = groupedGames.max()
        seasonMin = groupedGames.min()

        rankingDict[team]['seasonMean'] = seasonMean
        rankingDict[team]['seasonMax'] = seasonMax
        rankingDict[team]['seasonMin'] = seasonMin

    return rankingDict


def overall_metrics(rankDict):
    """
    Get rating summaries for all teams for each season.

    Parameters
    ----------
    rankDict : TYPE
        DESCRIPTION.

    Returns
    -------
    overallMetrics : TYPE
        DESCRIPTION.

    """
    # Parameters
    minGameThresh = 0

    # Prep
    overallMetrics = pd.DataFrame()

    # Convert rankingDict to multi-level dataframe
    # Columns: Season, Team, {rating [mean, max, min]}
    for team, value in rankDict.items():
        teamMetrics = pd.DataFrame()
        for metric, df in value.items():
            # Pull data from columns look at season summary stats
            if 'season' in metric:
                dfMetrics = df.copy()  # otherwise modifies input df in dict
                dfMetrics.columns = pd.MultiIndex.from_product(
                    [dfMetrics.columns, [metric]])
                # Build dataframe with all ranking methods and their season
                # summaries, for each season
                if teamMetrics.empty:
                    teamMetrics = dfMetrics
                else:
                    teamMetrics = pd.merge(
                        teamMetrics, dfMetrics, left_on='Season',
                        right_index=True, how='left', sort=False)

        # Clean up dataframe indicies
        teamMetrics.sort_index(axis=1, inplace=True)
        teamMetrics['Team'] = team
        teamMetrics.set_index(['Team'], append=True, inplace=True)
        # Add secondary info
        teamMetrics['gameCount'] = value['gameCount']

        # Add team's data to top level dataframe
        if overallMetrics.empty:
            overallMetrics = teamMetrics
        else:
            overallMetrics = overallMetrics.append(teamMetrics)

    # Sort idicies
    overallMetrics.sort_index(axis=0, inplace=True)
    # Filter out low game count teams
    filteredMetrics = overallMetrics[(
        overallMetrics.gameCount > minGameThresh)]

    # Create output metrics
    for season, seasonData in filteredMetrics.groupby(level=0):
        for col in seasonData:
            if 'Max' in col[1]:
                summaryData = seasonData.loc[:, col].max()
            if 'Min' in col[1]:
                summaryData = seasonData.loc[:, col].min()
            if 'Mean' in col[1]:
                summaryData = seasonData.loc[:, col].mean()

            overallMetrics.loc[(season, 'Average'), col] = summaryData

    overallMetrics.to_hdf('Overall_Metrics.h5', key='overallMetrics', mode='w')
    return overallMetrics
