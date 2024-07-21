import pandas as pd
import requests
import json
import os
from urllib.parse import quote
from datetime import datetime, timedelta
import time

# Load the configuration
with open('config.json', 'r') as f:
    config = json.load(f)

with open('schema.json', 'r') as f:
    schema = json.load(f)

# Define the save_json function to save the configuration file
def save_json(path, data):
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
            print("Configuration saved successfully.")
    except Exception as e:
        print(f"Error: Could not save the configuration to {path}. {str(e)}")

# Define the add_user function to add a new user to the configuration
def add_user(username):
    config['USER_EXTRACT_INFO'][username] = {
        'latest_match_date_str': ""
        , 'latest_match_date_epoch': None
        , 'number_matches': 0
    }
    save_json('config.json', config)

# Define the reset_config function to reset the configuration for a specific user
def reset_config():
    config['USER_EXTRACT_INFO'][RIOT_ID_NAME]['latest_match_date_str'] = ""
    config['USER_EXTRACT_INFO'][RIOT_ID_NAME]['latest_match_date_epoch'] = None
    config['USER_EXTRACT_INFO'][RIOT_ID_NAME]['number_matches'] = 0
    save_json('config.json', config)
    
# Define the update_latest_track_date function to update the latest match date and number of matches
def update_latest_track_date(date, number_matches):
        config['USER_EXTRACT_INFO'][RIOT_ID_NAME]['latest_match_date_epoch'] = date
        
        epoch_date_s = date / 1000 # Converting epoch date from milliseconds to seconds
        date_str = datetime.fromtimestamp(epoch_date_s).strftime('%Y-%m-%d %H:%M:%S')
        config['USER_EXTRACT_INFO'][RIOT_ID_NAME]['latest_match_date_str'] = date_str
        
        config['USER_EXTRACT_INFO'][RIOT_ID_NAME]['number_matches'] = number_matches
        save_json('config.json', config)

# Load the API key and user information from the configuration
API_KEY = config['API_KEY']
RIOT_ID_NAME = config['RIOT_ID_NAME']
TAG_LINE = config['TAG_LINE']
encoded_riot_id_name = quote(RIOT_ID_NAME)
encoded_tag_line = quote(TAG_LINE)

NEW_XLSX = config['NEW_XLSX']

PATH_MATCHES_DATA = config['path_matches_data'].replace('{username}', RIOT_ID_NAME)
PATH_KILLS_DATA = config['path_kills_data'].replace('{username}', RIOT_ID_NAME)
PATH_SPELLS_DATA = config['path_spells_data'].replace('{username}', RIOT_ID_NAME)

# Check if the user exists in the configuration, if not add the user
if RIOT_ID_NAME not in config['USER_EXTRACT_INFO']:
    add_user(RIOT_ID_NAME)
elif NEW_XLSX:
    reset_config()

# Load the latest match date and number of matches from the configuration
LATEST_MATCH_DATE_STR = config['USER_EXTRACT_INFO'][RIOT_ID_NAME]['latest_match_date_str']
LATEST_MATCH_DATE = config['USER_EXTRACT_INFO'][RIOT_ID_NAME]['latest_match_date_epoch']
number_matches = config['USER_EXTRACT_INFO'][RIOT_ID_NAME]['number_matches']

# Define the summoner region and API URL
SUMMONER_REGION = config['SUMMONER_REGION']
url = config['BASE_URL'].replace('{REGION}', SUMMONER_REGION).replace('{encoded_riot_id_name}', encoded_riot_id_name).replace('{encoded_tag_line}', encoded_tag_line)

# Set the request headers with the API key
headers = {
    'X-Riot-Token': API_KEY
}

# Fetch the summoner data
response = requests.get(url, headers=headers)
if response.status_code == 200:
    summoner_data = response.json()
    PUUID = summoner_data['puuid']
else:
    print(f'Error: {response.status_code}')
    

# Function to read an Excel file and return a DataFrame
def read_excel(path, schema=None):
    print('Reading Excel from: ', path)
    df = pd.read_excel(path)
    if schema:
        # Convert DataFrame columns to the specified data types
        for column, dtype in schema.items():
            print('Column :', column, 'dtype :', dtype)
            df[column] = df[column].astype(dtype)
    
    return df

# Function to save a DataFrame to an Excel file
def output_excel(path, df, schema=None, append=False):
    print('Outputting Excel to: ', path)
    if schema:
        # Convert DataFrame columns to the specified data types
        for column, dtype in schema.items():
            print('Column :', column, 'dtype :', dtype)
            df[column] = df[column].astype(dtype)
    
    if os.path.exists(path) and append:
        existing_df = read_excel(path=path, schema=schema)
        df = pd.concat([existing_df, df], ignore_index=True)
    
    df.to_excel(path, index=False)


# Function to fetch match IDs for a given PUUID and time range
def fetch_matches(puuid, start_time=None, end_time=None):
    
    match_ids = []
    start = 0
    count = 100
    
    while True:
        if start_time and end_time:
            url = (f'https://{SUMMONER_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{PUUID}/ids'
               f'?startTime={int(start_time.timestamp())}&endTime={int(end_time.timestamp())}&start={start}&count={count}')
        else:
            url = f'https://{SUMMONER_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{PUUID}/ids?start={start}&count={count}'
            
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            matches = response.json()
            if not matches:
                break
            match_ids.extend(matches)
            start += count
        else:
            print(f'Error: {response.status_code}')
            break
    
    return match_ids

# Function to get match data for a given match ID
def get_match_data(match_id):
    url = f'https://{SUMMONER_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        match_data = response.json()
        for participant in match_data['info']['participants']:
            if participant['puuid'] == PUUID:
                match_details = {
                    'match_id': match_id
                    , 'champion': participant['championName']
                    , 'duration': match_data['info']['gameDuration']  # Duration in seconds
                    , 'kills': participant['kills']
                    , 'deaths': participant['deaths']
                    , 'assists': participant['assists']
                    , 'win': 1 if participant['win'] else 0
                    , 'game_mode': match_data['info']['gameMode']
                    , 'queueId': match_data['info']['queueId']
                    , 'game_creation_date': match_data['info']['gameCreation']
                    , 'single_kills': participant['kills']
                    , 'double_kills': participant['doubleKills']
                    , 'triple_kills': participant['tripleKills']
                    , 'quadra_kills': participant['quadraKills']
                    , 'penta_kills': participant['pentaKills']
                    , 'skill_q_clicks': participant.get('spell1Casts', 0)
                    , 'skill_w_clicks': participant.get('spell2Casts', 0)
                    , 'skill_e_clicks': participant.get('spell3Casts', 0)
                    , 'skill_r_clicks': participant.get('spell4Casts', 0)
                }
                return match_details
    else:
        print(f'Error fetching match {match_id}: {response.status_code}')
        return None

# Function to merge and sum DataFrames based on key columns and sum columns
def merge_and_sum(existing_df, new_df, key_columns, sum_columns):
    if not existing_df.empty:
        combined_df = pd.concat([existing_df, new_df])
        combined_df = combined_df.groupby(key_columns, as_index=False)[sum_columns].sum()
        return combined_df
    else:
        return new_df


# Initialize lists to store match data
list_match_ids = []
matches_data = []
kills_data = []
spells_data = []


# Check if there was already extracted data
if os.path.exists(PATH_MATCHES_DATA) and not NEW_XLSX:
    existing_match_df = read_excel(PATH_MATCHES_DATA)
    
    start_time = datetime.fromtimestamp(LATEST_MATCH_DATE / 1000).strftime('%Y-%m-%d %H:%M:%S')
    list_match_ids = fetch_matches(PUUID, start_time=start_time)
    # Don't get data from matches already extracted
    list_match_ids = [m for m in list_match_ids if m not in list(existing_match_df['match_id'])]
else:
    list_match_ids = fetch_matches(PUUID)

print(f'Total Matches: {len(list_match_ids)}')


for match_id in list_match_ids:
    match_data = get_match_data(match_id)
    if match_data:
        number_matches += 1
        # Add data to matches_data
        matches_data.append({
            'match_id': match_data['match_id']
            , 'champion': match_data['champion']
            , 'duration': match_data['duration']
            , 'kills': match_data['kills']
            , 'deaths': match_data['deaths']
            , 'assists': match_data['assists']
            , 'win': match_data['win']
            , 'game_mode': match_data['game_mode']
            , 'queueId': match_data['queueId']
            , 'game_creation_date': match_data['game_creation_date']
        })

        # Add data to kills_data
        kill_types = ['single_kills', 'double_kills', 'triple_kills', 'quadra_kills', 'penta_kills']
        kill_labels = ['Single Kill', 'Double Kill', 'Triple Kill', 'Quadra Kill', 'Penta Kill']
        for kill_type, kill_label in zip(kill_types, kill_labels):
            kills_data.append({
                'Champion': match_data['champion']
                , 'Kill Type': kill_label
                , 'Number of Kills': match_data[kill_type]
            })

        # Add data to spells_data
        spells_types = ['skill_q_clicks', 'skill_w_clicks', 'skill_e_clicks', 'skill_r_clicks']
        spells_labels = ['Q', 'W', 'E', 'R']
        for spell_type, spell_label in zip(spells_types, spells_labels):
            spells_data.append({
                'Champion': match_data['champion']
                , 'Spell Type': spell_label
                , 'Spell Casts': match_data[spell_type]
            })

    # Sleep for 1.3 secs to avoid exceeding rate limit of API
    time.sleep(1.3)


matches_df = pd.DataFrame(matches_data)
kills_df = pd.DataFrame(kills_data)
spells_df = pd.DataFrame(spells_data)


# Load existing kills data
if os.path.exists(PATH_KILLS_DATA):
    existing_kills_df = read_excel(PATH_KILLS_DATA)
    # Merge kills data
    kills_df = merge_and_sum(existing_kills_df, kills_df, ['Champion', 'Kill Type'], ['Number of Kills'])

output_excel(PATH_KILLS_DATA, kills_df, append=False)
# else:
#     existing_kills_df = pd.DataFrame(columns=kills_df.columns)


# Load existing spells data
if os.path.exists(PATH_SPELLS_DATA):
    existing_spells_df = read_excel(PATH_SPELLS_DATA)
    # Merge spells data
    spells_df = merge_and_sum(existing_spells_df, spells_df, ['Champion', 'Spell Type'], ['Spell Casts'])

output_excel(PATH_SPELLS_DATA, spells_df, append=False)
# else:
#     existing_spells_df = pd.DataFrame(columns=spells_df.columns)


matches_schema = schema['Matches Data']

output_excel(PATH_MATCHES_DATA, matches_df, schema=matches_schema , append=not NEW_XLSX)


# Update the configuration with the latest match date and number of matches
latest_game_date = matches_df['game_creation_date'].max()

update_config = True
if update_config and matches_data:
    if not LATEST_MATCH_DATE or latest_game_date >= LATEST_MATCH_DATE:
        update_latest_track_date(date=latest_game_date, number_matches=number_matches)

