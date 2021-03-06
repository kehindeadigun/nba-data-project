try:
    import sys
    import zipfile
    import os
    import shutil
    import pandas as pd
    import numpy as np
    from pathlib import Path
    from sqlalchemy import create_engine
    from process_dataframes import process_teams_data, process_players_data
    from process_dataframes import process_ranking_data, process_games_data, process_stat_data
    from create_db import create_database
except:
    print('Some files may have import clashes.')

def is_path(filepath, checktype='dir'):
    """Checks if a path or directory exists.
    Args:
    filepath str: A string representing a path or directory.
    checktype str:  A string. Accepts values 'dir' for directory and 'file' for file. Default: 'dir'
    Returns:
    A boolean value: true if the path or directory exists and false otherwise.
    """
    if checktype == 'dir':
        if not os.path.isdir(filepath):
            print(f'WARNING: Directory {filepath} does not exist.')
            return False
    if checktype == 'file':
        if not os.path.isfile(filepath):
            print(f'WARNING: File {filepath} does not exist or not found.')
            return False
    return True

def check_inputs(inputs, file_types):
    """Checks if multiple inputs exist as files or directories.
        Uses the is_path function.
    Args:
    inputs list or array of strings: Contains all the directories to check.
        file_types list or array of strings: Contains the expected file type for each input.
        Each list value should be a string of value 'file' or 'dir'
    Returns:
    A boolean value: true only if the all path or directories exist and false otherwise.
    """
    for i, filepath in enumerate(inputs):
        if not is_path(filepath, file_types[i]):
            return False
    return True

def load_data(archive_filepath, extract_dir):
    """Loads archive file, extracts the data and loads in a list of dataframes.
    Args:
    archive_filepath str: The file path to the archive.zip file
    extract_dir str: The location to extract the zip file
    Returns:
    A dictionary with each key corresponding to a pandas dataframe.
    """
    #unzip the archive file
    with zipfile.ZipFile(archive_filepath, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
    #sort so file order is always consistent
    datasets = sorted([extract_dir+'/'+file_name for file_name in  os.listdir(extract_dir)])
    
    #reading in the data from the unzipped archive data
    game_df = pd.read_csv(datasets[0])
    stats_df = pd.read_csv(datasets[1])
    player_df = pd.read_csv(datasets[2])
    ranking_df = pd.read_csv(datasets[3])
    team_df = pd.read_csv(datasets[4])

    df_list = [team_df, player_df, ranking_df, game_df, stats_df]
    table_names = ['team', 'player', 'ranking', 'game', 'statistics']
    return dict(zip(table_names, df_list))


def clean_data(df_dict):
    """Cleans a dataframe
    Args:
    df pandas.Dataframe: A pandas dataframe to clean
    Returns:
    df_dict dict dictionary: Keys are the database/dataframe table names
              Objects are cleaned pandas dataframes.
    """
    #going down each key, we clean the dataframes in the dictionary
    df_dict['team'] = process_teams_data(df_dict['team'])
    [df_dict['player'], df_dict['season_player']] = process_players_data(df_dict['player'])
    df_dict['ranking'] = process_ranking_data(df_dict['ranking'])
    df_dict['game'] = process_games_data(df_dict['game'])
    df_dict['statistics'] = process_stat_data(df_dict['statistics'])
    return df_dict


def save_data(df_dict, database_filepath):
    """Save content of a dataframe to a database
    Args:
    df_dict pandas.Dataframe: A dictionary of pandas dataframes for
            which each value is saved to the database
    database_filepath str: A filepath for the database name
    Returns:
    A cleaned pandas dataframe.
    """
    create_database(database_filepath)
    engine = create_engine('sqlite:///'+database_filepath)
    for key in df_dict.keys():
        print(f'Writing to {key} table to {database_filepath}.....')
        df_dict[key].to_sql(f'{key}', engine, index=False, chunksize=20, method='multi', if_exists='append')

def del_filefolder(filefolder):
    """Deletes a file folder
    Args:
    filefolder str: A filefolder to delete
    """
    dirpath = Path(filefolder)
    if dirpath.exists() and dirpath.is_dir():
        shutil.rmtree(filefolder)

def main():
    """
    Main file
    Reads in the content of an archive file.
    Processes the archive.zip data files
    Extracts results to a database.
    """
    inputs = sys.argv
    file_types = ['file']
    extract_dir = 'xdataextract023456789'
    print('Startup...Verifying File paths.....')
    if (len(inputs) == 3) and check_inputs(inputs[1:-1], file_types):

        [archive_filepath, database_filepath] = inputs[1:]
        
        print('Loading data file {}......'.format(archive_filepath))
        df_dict = load_data(archive_filepath, extract_dir)

        print('Deleting the archive directory....')
        del_filefolder(extract_dir)

        print('Cleaning data.......')
        df_dict = clean_data(df_dict)

        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df_dict, database_filepath)

        print('Cleaned data saved to database!')
        print(f'Access your db at {database_filepath}')
    else:
        print('Please provide the filepath of the archive.zip '\
              'file as the first argument.\n Provide the filepath '\
              'of the database as the second argument. '\
              'Cleaned data will be saved there. '\
              '\nExample: python3 process_data.py path/to/archive.zip path/to/my.db')

if __name__ == '__main__':
    main()
