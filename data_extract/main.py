import pandas as pd
import os
from datetime import datetime
import logging

from config_manager import ConfigManager
from data_storage import DataStorage
from helper import Helper
from riot_api import RiotAPI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("main.log"),
        logging.StreamHandler()
    ]
)

class LolDataExtractor:
    def __init__(self, config_path: str, schema_path: str):
        self.config_manager = ConfigManager(config_path, schema_path)
        self.riot_api = RiotAPI(api_key=self.config_manager.API_KEY
                                , base_url=self.config_manager.BASE_URL
                                , username=self.config_manager.RIOT_ID_NAME)
        self.storage = DataStorage()
        self.helper = Helper()
        logging.basicConfig(level=logging.INFO)
        
    
    def run(self) -> None:
        # Initialize lists to store match data
        list_match_ids = []

        # Check if there was already extracted data
        if os.path.exists(self.config_manager.PATH_MATCHES_DATA) and not self.config_manager.NEW_XLSX:
            existing_match_df = self.storage.read_excel(self.config_manager.PATH_MATCHES_DATA)
            
            start_time = datetime.fromtimestamp(self.config_manager.LATEST_MATCH_DATE / 1000).strftime('%Y-%m-%d %H:%M:%S')
            list_match_ids = self.riot_api.fetch_matches(self.config_manager.PUUID, start_time=start_time)
            # Don't get data from matches already extracted
            list_match_ids = [m for m in list_match_ids if m not in list(existing_match_df['match_id'])]
        else:
            list_match_ids = self.riot_api.fetch_matches(self.config_manager.PUUID)

        logging.info(f'Total Matches: {len(list_match_ids)}')

        matches_data, kills_data, spells_data, damage_data, number_matches = self.riot_api.process_matches(list_match_ids)

        matches_df = pd.DataFrame(matches_data)
        kills_df = pd.DataFrame(kills_data)
        spells_df = pd.DataFrame(spells_data)
        damage_df = pd.DataFrame(damage_data)

        # Load existing kills data
        if os.path.exists(self.config_manager.PATH_KILLS_DATA):
            existing_kills_df = self.storage.read_excel(self.config_manager.PATH_KILLS_DATA)
            # Merge kills data
            kills_df = self.helper.merge_and_sum(existing_kills_df, kills_df, ['Champion', 'Kill Type'], ['Number of Kills'])


        # Load existing spells data
        if os.path.exists(self.config_manager.PATH_SPELLS_DATA):
            existing_spells_df = self.storage.read_excel(self.config_manager.PATH_SPELLS_DATA)
            # Merge spells data
            spells_df = self.helper.merge_and_sum(existing_spells_df, spells_df, ['Champion', 'Spell Type'], ['Spell Casts'])


        # Load existing damage data
        if os.path.exists(self.config_manager.PATH_DAMAGE_DATA):
            existing_damage_df = self.storage.read_excel(self.config_manager.PATH_DAMAGE_DATA)
            # Merge damage data
            damage_df = self.helper.merge_and_sum(existing_damage_df, damage_df, ['Champion', 'Damage Type'], ['Damage Amount'])


        matches_schema = self.config_manager.schema['Match Data']

        self.storage.output_excel(self.config_manager.PATH_KILLS_DATA, kills_df, append=False)
        self.storage.output_excel(self.config_manager.PATH_SPELLS_DATA, spells_df, append=False)
        self.storage.output_excel(self.config_manager.PATH_DAMAGE_DATA, damage_df, append=False)
        self.storage.output_excel(self.config_manager.PATH_MATCHES_DATA, matches_df, schema=matches_schema , append=not self.config_manager.NEW_XLSX)


        # Update the configuration with the latest match date and number of matches
        latest_game_date = matches_df['game_creation_date_epoch'].max()

        update_config = True
        if update_config and matches_data:
            if not self.config_manager.LATEST_MATCH_DATE or latest_game_date >= self.config_manager.LATEST_MATCH_DATE:
                self.config_manager.update_latest_track_date(date=latest_game_date, number_matches=number_matches)

if __name__ == 'main':
    extractor = LolDataExtractor('config.json', 'schema.json')
    # extractor.run()