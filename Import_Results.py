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
import h5py
import requests
import os

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

    for seasonStart in range(yearStart, yearEnd):
        season = str(seasonStart) + str(seasonStart+1)
        chnURL = chnFullSeason + season
        chnTables = pd.read_html(chnURL, skiprows=1)
        seasonResults = chnTables[-1]

        seasonResults = seasonResults.astype(str)

        with pickle_protocol(2):
            seasonResults.to_hdf(outputFile,
                                 key='y' + season, mode='a')

        time.sleep(0.3)  # Don't hammer CHN to fast
        print(seasonStart)

    print('Results download complete.')


def clean_results(fileName):
    """
    Clean up downloaded results from CHN.

    Parameters
    ----------
    fileName : str
        File name and path of raw results from CHN, saved as HDF.

    Returns
    -------
    Saves cleaned composite results to HDF.

    """
    # Setup
    outputFile = 'Data/Results_Composite.h5'

    headers = ['Away', 'Away_Score', 'Location', 'Home', 'Home_Score',
               'OT', 'Time', 'Notes_1', 'drop', 'Notes_2']

    resultsOutput = pd.DataFrame()

    # Loop through each season
    for season in h5py.File(fileName, 'r').keys():
        # Get season results
        seasonRaw = pd.read_hdf(fileName, key=season)

        # ------ Clean up data ------
        # Remove all the extra columns
        resultsCleaned = seasonRaw[seasonRaw.columns[0:len(headers)]]
        resultsCleaned.columns = headers
        resultsCleaned = resultsCleaned.drop(columns=['drop'])

        # Remove rows without data
        resultsCleaned = resultsCleaned[pd.notnull(resultsCleaned['Away'])]
        resultsCleaned = resultsCleaned.reset_index(drop=True)

        # Add game date column
        dates = pd.to_datetime(resultsCleaned.Away, errors='coerce')
        dates_ffill = dates.fillna(method='ffill')
        resultsCleaned['Date'] = dates_ffill

        # Remove rows of dates
        resultsCleaned = resultsCleaned[pd.isna(dates)]
        resultsCleaned = resultsCleaned.reset_index(drop=True)

        # Clean games without scores
        scorelessGamesAway = pd.isnull(resultsCleaned['Away_Score'])
        scorelessGamesHome = pd.isnull(resultsCleaned['Home_Score'])
        scorelessGames = scorelessGamesAway | scorelessGamesHome
        missingScores = np.where(scorelessGames)[0]
        resultsCleaned = resultsCleaned.drop(missingScores)

        # Determine Conference
        conf_isdigit = resultsCleaned['Away_Score'].str.isdigit()
        conf_isdigit = conf_isdigit.fillna(False)
        conf_isdigit = ~conf_isdigit
        conf_score = resultsCleaned['Away_Score']
        conf = conf_score[conf_isdigit]
        resultsCleaned['Conference'] = conf
        resultsCleaned['Conference'] = resultsCleaned['Conference'].fillna(
            method='ffill')
        resultsCleaned = resultsCleaned[~conf_isdigit]

        # Add Season to Each Game
        resultsCleaned['Season'] = str(season[1:5])

        # Sort Games by date
        resultsCleaned = resultsCleaned.sort_values(by=['Date'])

        resultsOutput = resultsOutput.append(resultsCleaned)


    # Set Data types for ech column
    resultsOutput['Season'] = resultsOutput['Season'].astype(int)
    resultsOutput['Home_Score'] = resultsOutput['Home_Score'].astype(int)
    resultsOutput['Away_Score'] = resultsOutput['Away_Score'].astype(int)

    # Wrtie to HDF
    with pickle_protocol(2):
        resultsOutput.to_hdf(outputFile,
                             key='resultsComposite', mode='a')


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

    resultsShrink = results[(results.Season >= int(startYear)) &
                            (results.Season <= int(endYear))]

    print('Results limited to ', str(startYear), ' through ', str(endYear))
    print('Results shape: ', resultsShrink.shape)
    return resultsShrink


def load_composite_results(location='local'):
    """
    Read composite results file into workspace.

    Parameters
    ----------
    location : file path, optional
        Full path to HDF file of composite results.
        The default is 'local', file in project folder.

    Returns
    -------
    resultsFull : pandas dataframe

    """
    if location == 'local':
        resultsFull = pd.read_hdf('Data/Results_Composite.h5')
    else:
        # resultsFull = pd.read_hdf(location)
        r = requests.get(location)
        with open('temp.h5', 'wb') as f:
            f.write(r.content)
        resultsFull = pd.read_hdf('temp.h5')
        os.remove('temp.h5')

    print('Results shape: ', resultsFull.shape)
    return resultsFull


# %% Run as script
if __name__ == '__main__':

    def valid_year_input(year, firstYear=0):
        """
        Verify years to download are reasonable.

        Returns
        -------
        True/False

        """
        try:
            year = int(year)
            firstYear = int(firstYear)
        except ValueError:
            print('Give me a real number')
            return False

        if not len(str(year)) == 4:
            print('Enter 4 digit year')
            return False
        if year < 1900:
            print('Hockey wasn\'t invented then')
            return False
        if year > date.today().year:
            print('Time traveling is not allowed')
            return False
        if year <= firstYear:
            print(f'Pick year greater than {firstYear}')
            return False

        return True

    def download_results():
        """Download CHN results."""
        startYear = input('Start Year: ')
        while not valid_year_input(startYear):
            startYear = input('Start Year: ')

        endYear = input('End Year: ')
        while not valid_year_input(endYear, startYear):
            endYear = input('End Year: ')

        download_results_CHN(int(startYear), int(endYear),
                             dataFolder, gameDataRaw)

    if input('Download Results? [y] ') == 'y':
        download_results()
        clean_results(dataFolder + gameDataRaw)
    elif input('Clean results? [y] ') =='y':
        clean_results(dataFolder + gameDataRaw)

    resultsComposite = load_composite_results()
