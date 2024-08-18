import json
import os
from urllib.parse import quote
import requests
import logging

from helper import Helper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("config_manager.log"),
        logging.StreamHandler()
    ]
)

class ConfigManager:
    def __init__(self, config_path='config.json', schema_path='schema.json'):
        self.config_path = config_path 
        self.schema_path = schema_path
        self.config = self.load_json(config_path)
        self.schema = self.load_json(schema_path)

        self.NEW_XLSX = self.config['NEW_XLSX']

        self.RIOT_ID_NAME = self.config['RIOT_ID_NAME']
        if self.RIOT_ID_NAME not in self.config['USER_EXTRACT_INFO']:
            self.add_user(self.RIOT_ID_NAME)
        elif self.NEW_XLSX:
            self.reset_config()

        self.LATEST_MATCH_DATE_STR = self.config['USER_EXTRACT_INFO'][self.RIOT_ID_NAME]['latest_match_date_str']
        self.LATEST_MATCH_DATE = self.config['USER_EXTRACT_INFO'][self.RIOT_ID_NAME]['latest_match_date_epoch']
        self.NUMBER_MATCHES = self.config['USER_EXTRACT_INFO'][self.RIOT_ID_NAME]['number_matches']

        self.API_KEY = self.config['API_KEY']
        self.RIOT_ID_NAME = self.config['RIOT_ID_NAME']
        self.SUMMONER_REGION = self.config['SUMMONER_REGION']
        self.TAG_LINE = self.config['TAG_LINE']
        self.encoded_riot_id_name = quote(self.RIOT_ID_NAME)
        self.encoded_tag_line = quote(self.TAG_LINE)
        self.BASE_URL = self.config['BASE_URL'].replace('{REGION}', self.SUMMONER_REGION).replace('{encoded_riot_id_name}', self.encoded_riot_id_name).replace('{encoded_tag_line}', self.encoded_tag_line)

        self.headers = { 'X-Riot-Token': self.API_KEY }
        response = requests.get(self.BASE_URL, headers=self.headers)
        if response.status_code == 200:
            summoner_data = response.json()
            self.PUUID = summoner_data['puuid'] # PUUID is the global unique player Riot ID
        else:
            self.PUUID = None
            logging.error(f'Error: {response.status_code}')

        self.PATH_MATCHES_DATA = self.config['path_matches_data'].replace('{username}', self.RIOT_ID_NAME)
        self.PATH_KILLS_DATA = self.config['path_kills_data'].replace('{username}', self.RIOT_ID_NAME)
        self.PATH_SPELLS_DATA = self.config['path_spells_data'].replace('{username}', self.RIOT_ID_NAME)
        self.PATH_DAMAGE_DATA = self.config['path_damage_data'].replace('{username}', self.RIOT_ID_NAME)

        self.SLEEP_DURATION = self.config['SLEEP_DURATION']
        self.MATCH_FETCH_COUNT = self.config['MATCH_FETCH_COUNT']

    def load_json(self, path):
        try:
            with open(path) as f:
                return json.load(f)
        
        except FileNotFoundError:
            logging.error(f"Error: The file {path} does not exist.")
            return {}
        except json.JSONDecodeError:
            logging.error(f"Error: The file {path} is not a valid JSON.")
            return {}
        
    def save_json(self, path, data):
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
                logging.info('Configuration saved successfully')
        except Exception as e:
            logging.error(f"Error: Could not save the configuration to {path}. {str(e)}")

    def add_user(self, username):
        self.config['USER_EXTRACT_INFO'][username] = {
            'latest_match_date_str': ""
            , 'latest_match_date_epoch': None
            , 'number_matches': 0
        }
        self.save_json('config.json', self.config)

    def reset_config(self):
        self.config['USER_EXTRACT_INFO'][self.RIOT_ID_NAME]['latest_match_date_str'] = ""
        self.config['USER_EXTRACT_INFO'][self.RIOT_ID_NAME]['latest_match_date_epoch'] = None
        self.config['USER_EXTRACT_INFO'][self.RIOT_ID_NAME]['number_matches'] = 0
        self.save_json('config.json', self.config)

    def update_latest_track_date(self, date, number_matches):
            self.config['USER_EXTRACT_INFO'][self.RIOT_ID_NAME]['latest_match_date_epoch'] = date
            
            date_str = Helper().date_from_epoch(date)
            self.config['USER_EXTRACT_INFO'][self.RIOT_ID_NAME]['latest_match_date_str'] = date_str
            
            self.config['USER_EXTRACT_INFO'][self.RIOT_ID_NAME]['number_matches'] = number_matches
            self.save_json('config.json', self.config)
        

