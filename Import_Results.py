# -*- coding: utf-8 -*-
"""
Download and Import Hockey Results.

@author: Scott
"""
# Setup

import pandas as pd
import numpy as np
import time


def download_results_CHN(yearStart=1900, yearEnd=2020):
    """
    Download results from CHN.

    Parameters
    ----------
    yearStart : TYPE, optional
        DESCRIPTION. The default is 1900.
    yearEnd : TYPE, optional
        DESCRIPTION. The default is 2020.

    Returns
    -------
    None.

    """
    # Import CHN webpages
    year_start = 1900
    year_end = 2019

    chn_season_url = 'https://www.collegehockeynews.com/schedules/index.php?rtz=0&season='

    # results_composite = pd.DataFrame

    for season_start in range(year_start, year_end):
        season = str(season_start) + str(season_start+1)
        chn_url = chn_season_url + season
    #     print(chn_url)
        chn_tables = pd.read_html(chn_url, skiprows=1)
        season_results = chn_tables[-1]
        if season_start == year_start:
            chn_composite = season_results
        else:
            chn_composite = chn_composite.append(season_results,
                                                 ignore_index=True)
        time.sleep(0.3)
        print(season_start)

    print(chn_composite.shape)

    # Write to CSV
    chn_composite.to_csv(path_or_buf='CHN_Raw.csv', index=False)


def clean_results(fileName='CHN_Raw.csv'):
    """
    Clean up downloaded results from CHN.

    Parameters
    ----------
    fileName : TYPE, optional
        DESCRIPTION. The default is 'CHN_Raw.csv'.

    Returns
    -------
    None.

    """
    # Import CHN raw results
    results_composite = pd.read_csv('CHN_Raw.csv')
    print(results_composite.shape)

    # Clean up data

    headers = ['Away', 'Away Score', 'Location', 'Home', 'Home Score',
               'OT', 'nan', 'Notes']

    # Remove all the extra columns
    results_cleaned = results_composite[results_composite.columns[0:8]]
    results_cleaned.columns = headers
    results_cleaned = results_cleaned.drop(columns=['nan'])

    # Remove rows without data
    # print(pd.notnull(results_cleaned['Away']))
    results_cleaned = results_cleaned[pd.notnull(results_cleaned['Away'])]
    results_cleaned = results_cleaned.reset_index(drop=True)

    # Add game date column
    dates = pd.to_datetime(results_cleaned.Away, errors='coerce')
    # print(type(dates))
    # print(dates)
    # print(pd.isna(dates))
    dates_ffill = dates.fillna(method='ffill')
    results_cleaned['Date'] = dates_ffill

    # Remove rows of dates
    results_cleaned = results_cleaned[pd.isna(dates)]
    results_cleaned = results_cleaned.reset_index(drop=True)

    # Clean games without scores
    scorelessGamesAway = pd.isnull(results_cleaned['Away Score'])
    scorelessGamesHome = pd.isnull(results_cleaned['Home Score'])
    scorelessGames = scorelessGamesAway | scorelessGamesHome
    missingScores = np.where(scorelessGames)[0]
    # print(missingScores)
    # print(scorelessGames[missingScores])
    results_cleaned = results_cleaned.drop(missingScores)
    # print(results_cleaned.shape)

    # Determine Conference
    conf_isdigit = results_cleaned['Away Score'].str.isdigit()
    conf_isdigit = conf_isdigit.fillna(False)
    # print(conf_isdigit.unique())

    conf_isdigit = ~conf_isdigit
    conf_score = results_cleaned['Away Score']
    # print(conf_isdigit)
    conf = conf_score[conf_isdigit]
    # print(type(conf))
    # print(conf)
    results_cleaned['Conference'] = conf
    results_cleaned['Conference'] = results_cleaned['Conference'].fillna(method='ffill')
    results_cleaned = results_cleaned[~conf_isdigit]

    # Add Season to Each Game
    results_cleaned['Season'] = pd.PeriodIndex(results_cleaned['Date'],
                                               freq='A-Jul')

    # Sort Games by date
    results_cleaned = results_cleaned.sort_values(by=['Date'])

    print(results_cleaned.shape)
    # print(results_cleaned)

    # Write to CSV
    results_cleaned.to_csv(path_or_buf='Results_Composite.csv', index='False')
