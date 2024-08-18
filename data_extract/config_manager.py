import json
import os
from urllib.parse import quote

from helper import Helper

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

        self.url = self.config['BASE_URL'].replace('{REGION}', self.SUMMONER_REGION).replace('{encoded_riot_id_name}', self.encoded_riot_id_name).replace('{encoded_tag_line}', self.encoded_tag_line)

    def load_json(self, path):
        try:
            with open(path) as f:
                return json.load(f)
        
        except FileNotFoundError:
            print(f"Error: The file {path} does not exist.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: The file {path} is not a valid JSON.")
            return {}
        
    def save_json(self, path, data):
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
                print('Configuration saved successfully')
        except Exception as e:
            print(f"Error: Could not save the configuration to {path}. {str(e)}")

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
        

