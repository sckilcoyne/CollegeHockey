# -*- coding: utf-8 -*-
"""
Download and Import Hockey Results.

@author: Scott
"""
# %% Setup
# Standard Modules
import pandas as pd
import numpy as np
import time
from datetime import date


# Custom Modules
from utils.ForcePickle import pickle_protocol

# %% Files
dataFolder = 'Data/'

gameDataRaw = 'Results_CHN.h5'
gameData = 'Results_Composite.h5'

# %% Generate Results Data


def download_results_CHN(yearStart, yearEnd, outputFolder, outputFileName):
    """
    Download results from CHN.

    Parameters
    ----------
    yearStart : TYPE, optional
        DESCRIPTION. The default is 1900.
    yearEnd : TYPE, optional
        DESCRIPTION. The default is 2021.

    Returns
    -------
    None.
    Saves full composite results to /Data/ folder.

    """
    outputFile = outputFolder + outputFileName
    print(outputFile)

    # Import CHN webpages
    chnScheduleURL = 'https://www.collegehockeynews.com/schedules/index.php'
    selectSeason = '?rtz=0&season='
    chnFullSeason = chnScheduleURL + selectSeason

    # results_composite = pd.DataFrame

    for seasonStart in range(yearStart, yearEnd):
        season = str(seasonStart) + str(seasonStart+1)
        chnURL = chnFullSeason + season
    #     print(chn_url)
        chnTables = pd.read_html(chnURL, skiprows=1)
        seasonResults = chnTables[-1]
        # if seasonStart == yearStart:
        #     compositeResults = seasonResults
        # else:
        #     compositeResults = compositeResults.append(seasonResults,
        #                                                ignore_index=True)

        with pickle_protocol(2):
            seasonResults.to_hdf(outputFile,
                                 key='y' + season, mode='a')

        time.sleep(0.3)  # Don't hammer CHN to fast
        print(seasonStart)

    # print(compositeResults.shape)

    # # Write to CSV
    # compositeResults.to_csv(path_or_buf='CHN_Raw.csv', index=False)

    # # Write to HDF
    # with pickle_protocol(2):
    #     compositeResults.to_hdf(outputFolder + outputFile,
    #                             key='raw_CHN_results', mode='w')


def clean_results(fileName):
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
    results_composite = pd.read_csv(fileName)
    print(results_composite.shape)

    # Clean up data

    headers = ['Away', 'Away_Score', 'Location', 'Home', 'Home_Score',
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
    scorelessGamesAway = pd.isnull(results_cleaned['Away_Score'])
    scorelessGamesHome = pd.isnull(results_cleaned['Home_Score'])
    scorelessGames = scorelessGamesAway | scorelessGamesHome
    missingScores = np.where(scorelessGames)[0]
    # print(missingScores)
    # print(scorelessGames[missingScores])
    results_cleaned = results_cleaned.drop(missingScores)
    # print(results_cleaned.shape)

    # Determine Conference
    conf_isdigit = results_cleaned['Away_Score'].str.isdigit()
    conf_isdigit = conf_isdigit.fillna(False)
    # print(conf_isdigit.unique())

    conf_isdigit = ~conf_isdigit
    conf_score = results_cleaned['Away_Score']
    # print(conf_isdigit)
    conf = conf_score[conf_isdigit]
    # print(type(conf))
    # print(conf)
    results_cleaned['Conference'] = conf
    results_cleaned['Conference'] = results_cleaned['Conference'].fillna(
        method='ffill')
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


# %% Working with results data
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
    resultsShrink = results[(results.Season >= startYear) &
                            (results.Season <= endYear)]

    print('Results limited to ', str(startYear), ' through ', str(endYear))
    print('Results shape: ', resultsShrink.shape)
    return resultsShrink


def load_composite_results(location='local'):
    """
    Read composite results file into workspace.

    Parameters
    ----------
    location : TYPE, optional
        DESCRIPTION. The default is 'local'.

    Returns
    -------
    resultsFull : TYPE
        DESCRIPTION.

    """
    if location == 'local':
        resultsFull = pd.read_csv('Results_Composite.csv')
    else:
        resultsFull = pd.read_csv(location)

    print('Results shape: ', resultsFull.shape)
    return resultsFull


# %% Run as script
if __name__ == '__main__':

    def valid_user_input(year, firstYear=0):
        """
        Verify years to download are reasonable.

        Returns
        -------
        True/False

        """
        if not len(str(year)) == 4:
            print('Enter 4 digit year')
            return False
        if year < 1900:
            print('Hockey wasn\'t invented then')
            return False
        if year > date.today().year:
            print('Time traveling is not allowed')
            return False
        if year < firstYear:
            print(f'Pick year greater than {firstYear}')
            return False
        return True

    startYear = int(input('Start Year: '))
    while not valid_user_input(startYear):
        startYear = int(input('Start Year: '))

    endYear = int(input('End Year: '))
    while not valid_user_input(endYear, startYear):
        endYear = int(input('End Year: '))

    download_results_CHN(startYear, endYear, dataFolder, gameDataRaw)
