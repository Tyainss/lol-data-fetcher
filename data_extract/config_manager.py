import json
import os
from urllib.parse import quote
import requests
import logging

from helper import Helper
from api_utils import make_request

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("config_manager.log"),
        logging.StreamHandler()
    ]
)

class ConfigManager:
    CONFIG_PATH_DEFAULT = 'config.json'
    SCHEMA_PATH_DEFAULT = 'schema.json'
    USER_EXTRACT_INFO_KEY = 'USER_EXTRACT_INFO'
    NEW_XLSX_KEY = 'NEW_XLSX'
    RIOT_ID_NAME_KEY = 'RIOT_ID_NAME'
    API_KEY_KEY = 'API_KEY'
    SUMMONER_REGION_KEY = 'SUMMONER_REGION'
    TAG_LINE_KEY = 'TAG_LINE'
    BASE_URL_KEY = 'BASE_URL'
    PATH_MATCHES_DATA_KEY = 'path_matches_data'
    PATH_KILLS_DATA_KEY = 'path_kills_data'
    PATH_SPELLS_DATA_KEY = 'path_spells_data'
    PATH_DAMAGE_DATA_KEY = 'path_damage_data'
    SLEEP_DURATION_KEY = 'SLEEP_DURATION'
    MATCH_FETCH_COUNT_KEY = 'MATCH_FETCH_COUNT'

    def __init__(self, config_path: str = CONFIG_PATH_DEFAULT, schema_path: str = SCHEMA_PATH_DEFAULT):
        self.config_path = config_path 
        self.schema_path = schema_path
        self.config = self.load_json(config_path)
        self.schema = self.load_json(schema_path)

        self.initialize_config()
        self.initialize_api()
        self.initialize_paths()
        self.initialize_other_settings()

    def initialize_config(self) -> None:
        self.NEW_XLSX = self.config[self.NEW_XLSX_KEY]
        self.RIOT_ID_NAME = self.config[self.RIOT_ID_NAME_KEY]
        if self.RIOT_ID_NAME not in self.config[self.USER_EXTRACT_INFO_KEY]:
            self.add_user(self.RIOT_ID_NAME)
        elif self.NEW_XLSX:
            self.reset_config()

        user_info = self.config[self.USER_EXTRACT_INFO_KEY][self.RIOT_ID_NAME]
        self.LATEST_MATCH_DATE_STR = user_info['latest_match_date_str']
        self.LATEST_MATCH_DATE = user_info['latest_match_date_epoch']
        self.NUMBER_MATCHES = user_info['number_matches']

    def initialize_api(self) -> None:
        self.API_KEY = self.config[self.API_KEY_KEY]
        self.SUMMONER_REGION = self.config[self.SUMMONER_REGION_KEY]
        self.TAG_LINE = self.config[self.TAG_LINE_KEY]
        self.encoded_riot_id_name = quote(self.RIOT_ID_NAME)
        self.encoded_tag_line = quote(self.TAG_LINE)
        self.BASE_URL = self.config[self.BASE_URL_KEY].replace('{REGION}', self.SUMMONER_REGION).replace('{encoded_riot_id_name}', self.encoded_riot_id_name).replace('{encoded_tag_line}', self.encoded_tag_line)

        self.headers = { 'X-Riot-Token': self.API_KEY }
        response = make_request(self.BASE_URL, headers=self.headers)
        # response = requests.get(self.BASE_URL, headers=self.headers)
        if response.status_code == 200:
            summoner_data = response.json()
            self.PUUID = summoner_data['puuid'] # PUUID is the global unique player Riot ID
        else:
            self.PUUID = None
            logging.error(f'Error: {response.status_code} - {response.text}')

    def initialize_paths(self) -> None:
        self.PATH_MATCHES_DATA = self.config[self.PATH_MATCHES_DATA_KEY].replace('{username}', self.RIOT_ID_NAME)
        self.PATH_KILLS_DATA = self.config[self.PATH_KILLS_DATA_KEY].replace('{username}', self.RIOT_ID_NAME)
        self.PATH_SPELLS_DATA = self.config[self.PATH_SPELLS_DATA_KEY].replace('{username}', self.RIOT_ID_NAME)
        self.PATH_DAMAGE_DATA = self.config[self.PATH_DAMAGE_DATA_KEY].replace('{username}', self.RIOT_ID_NAME)

    def initialize_other_settings(self) -> None:
        self.SLEEP_DURATION = self.config[self.SLEEP_DURATION_KEY]
        self.MATCH_FETCH_COUNT = self.config[self.MATCH_FETCH_COUNT_KEY]

    def load_json(self, path: str) -> dict:
        try:
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Error: The file {path} does not exist.")
            return {}
        except json.JSONDecodeError:
            logging.error(f"Error: The file {path} is not a valid JSON.")
            return {}
        
    def save_json(self, path: str, data: dict) -> None:
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
                logging.info('Configuration saved successfully')
        except Exception as e:
            logging.error(f"Error: Could not save the configuration to {path}. {str(e)}")

    def add_user(self, username: str) -> None:
        self.config[self.USER_EXTRACT_INFO_KEY][username] = {
            'latest_match_date_str': ""
            , 'latest_match_date_epoch': None
            , 'number_matches': 0
        }
        self.save_json(self.config_path, self.config)

    def reset_config(self) -> None:
        self.config[self.USER_EXTRACT_INFO_KEY][self.RIOT_ID_NAME]['latest_match_date_str'] = ""
        self.config[self.USER_EXTRACT_INFO_KEY][self.RIOT_ID_NAME]['latest_match_date_epoch'] = None
        self.config[self.USER_EXTRACT_INFO_KEY][self.RIOT_ID_NAME]['number_matches'] = 0
        self.save_json(self.config_path, self.config)

    def update_latest_track_date(self, date: int, number_matches: int) -> None:
        self.config[self.USER_EXTRACT_INFO_KEY][self.RIOT_ID_NAME]['latest_match_date_epoch'] = date
        date_str = Helper().date_from_epoch(date)
        self.config[self.USER_EXTRACT_INFO_KEY][self.RIOT_ID_NAME]['latest_match_date_str'] = date_str
        self.config[self.USER_EXTRACT_INFO_KEY][self.RIOT_ID_NAME]['number_matches'] = number_matches
        self.save_json(self.config_path, self.config)