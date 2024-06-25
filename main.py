import pandas as pd
import requests
import json
import os
from urllib.parse import quote
from datetime import datetime, timedelta
import time

with open('config.json', 'r') as f:
    config = json.load(f)

API_KEY = config['API_KEY']
RIOT_ID_NAME = config['RIOT_ID_NAME']
TAG_LINE = config['TAG_LINE']
encoded_riot_id_name = quote(RIOT_ID_NAME)
encoded_tag_line = quote(TAG_LINE)

PATH_MATCHES_DATA = config["path_matches_data"].replace('{username}', RIOT_ID_NAME)
PATH_KILLS_DATA = config["path_kills_data"].replace('{username}', RIOT_ID_NAME)
PATH_SPELLS_DATA = config["path_spells_data"].replace('{username}', RIOT_ID_NAME)

SUMMONER_REGION = config['SUMMONER_REGION']

url = config['BASE_URL'].replace('{REGION}', SUMMONER_REGION).replace('{encoded_riot_id_name}', encoded_riot_id_name).replace('{encoded_tag_line}', encoded_tag_line)

headers = {
    'X-Riot-Token': API_KEY
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    summoner_data = response.json()
    PUUID = summoner_data['puuid']
else:
    print(f'Error: {response.status_code}')
    

# Get data from matches

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


def get_match_data(match_id):
    url = f'https://{SUMMONER_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}'
    # headers = {'X-Riot-Toekn': API_KEY}
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


list_match_ids = []

# end_date = datetime.utcnow()
# start_date = end_date - timedelta(days=1*365)
# end_date = datetime(2023, 7, 21)
# start_date = datetime(2020, 1, 1)


# current_end_date = end_date

# while current_end_date > start_date:
#     current_start_date = current_end_date - timedelta(days=30)  # Fetch 30 days of matches at a time
#     if current_start_date < start_date:
#         current_start_date = start_date

#     batch_match_ids = fetch_matches(PUUID, current_start_date, current_end_date)
#     list_match_ids.extend(batch_match_ids)
#     current_end_date = current_start_date

list_match_ids = fetch_matches(PUUID)

print(f'Total Matches: {len(list_match_ids)}')


matches_data = []
kills_data = []
spells_data = []

for match_id in list_match_ids:
    match_data = get_match_data(match_id)
    if match_data:
        # Add data to matches_data
        matches_data.append({
            'match_id': match_data['match_id']
            , 'champion': match_data['champion']
            , 'duration': match_data['duration']
            , 'kills': match_data['kills']
            , 'deaths': match_data['deaths']
            , 'assists': match_data['assists']
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


# Export data
def read_excel(self, path, schema=None):
    print('Reading Excel from: ', path)
    df = pd.read_excel(path)
    if schema:
        # Convert DataFrame columns to the specified data types
        for column, dtype in schema.items():
            print('Column :', column, 'dtype :', dtype)
            df[column] = df[column].astype(dtype)
    
    return df


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


output_excel(PATH_MATCHES_DATA, matches_df)
output_excel(PATH_KILLS_DATA, kills_df)
output_excel(PATH_SPELLS_DATA, spells_df)
