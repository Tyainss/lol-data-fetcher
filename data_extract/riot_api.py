import requests
from datetime import datetime
import time
import logging
from typing import Optional, List, Dict, Any, Tuple

from helper import Helper
from config_manager import ConfigManager
from api_utils import make_request

# Import the logging configuration
from logging_config import setup_logging

# Set up logging
logger = setup_logging()

class RiotAPI:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.helper = Helper()
    
    def fetch_matches_list(self, puuid: Optional[str] = None, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[str]:
        match_ids = []
        start = 0
        count = self.config_manager.MATCH_FETCH_COUNT
        
        while True:
            url = (f'https://{self.config_manager.SUMMONER_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{self.config_manager.PUUID}/ids'
                   f'?start={start}&count={count}')
            if start_time and end_time:
                url += f'&startTime={int(start_time.timestamp())}&endTime={int(end_time.timestamp())}'
            #     url = (f'https://{self.config_manager.SUMMONER_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{self.config_manager.PUUID}/ids'
            #     f'?startTime={int(start_time.timestamp())}&endTime={int(end_time.timestamp())}&start={start}&count={count}')
            # else:
            #     url = f'https://{self.config_manager.SUMMONER_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{self.config_manager.PUUID}/ids?start={start}&count={count}'
                
            response = make_request(url, self.config_manager.headers)
            # response = requests.get(url, headers=self.config_manager.headers)
            
            if response.status_code == 200:
                matches = response.json()
                if not matches:
                    break
                match_ids.extend(matches)
                start += count
            else:
                logger.error(f'Error: {response.status_code}')
                break
        
        return match_ids
    
    def fetch_match_info(self, match_id: str) -> Optional[Dict[str, Any]]:
        url = f'https://{self.config_manager.SUMMONER_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}'
        response = make_request(url, self.config_manager.headers)
        # response = requests.get(url, headers=self.config_manager.headers)
        
        if response.status_code == 200:
            match_data = response.json()
            for participant in match_data['info']['participants']:
                if participant['puuid'] == self.config_manager.PUUID:
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
                        , 'ad_damage': participant['physicalDamageDealt']
                        , 'ap_damage': participant['magicDamageDealt']
                        , 'true_damage': participant['trueDamageDealt']                    
                    }
                    return match_details
        else:
            logger.error(f'Error fetching match {match_id}: {response.status_code}')
            return None
        
    def process_matches(self, list_match_ids: List[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], int]:
        matches_data = []
        kills_data = []
        spells_data = []
        damage_data = []
        number_matches = self.config_manager.NUMBER_MATCHES

        for match_id in list_match_ids:
            match_data = self.fetch_match_info(match_id)
            if match_data:
                number_matches += 1
                # Add data to matches_data
                matches_data.append({
                    'match_id': match_data['match_id']
                    , 'username': self.config_manager.RIOT_ID_NAME
                    , 'champion': match_data['champion']
                    , 'duration': match_data['duration']
                    , 'kills': match_data['kills']
                    , 'deaths': match_data['deaths']
                    , 'assists': match_data['assists']
                    , 'win': match_data['win']
                    , 'game_mode': match_data['game_mode']
                    , 'queueId': match_data['queueId']
                    , 'game_creation_date_epoch': match_data['game_creation_date']
                    , 'game_creation_date': self.helper.date_from_epoch(match_data['game_creation_date'])
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

                # Add data to damage_data
                damage_types = ['ad_damage', 'ap_damage', 'true_damage']
                damage_labels = ['AD Damage', 'AP Damage', 'True Damage']
                for damage_type, damage_label in zip(damage_types, damage_labels):
                    damage_data.append({
                        'Champion': match_data['champion']
                        , 'Damage Type': damage_label
                        , 'Damage Amount': match_data[damage_type]
                    })

            # Sleep for 1.3 secs to avoid exceeding rate limit of API
            time.sleep(self.config_manager.SLEEP_DURATION)
        
        return matches_data, kills_data, spells_data, damage_data, number_matches