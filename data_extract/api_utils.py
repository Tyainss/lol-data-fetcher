import requests
import time
import logging

def make_request(url: str, headers: dict) -> requests.Response:
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 429:  # Rate limit exceeded
            retry_after = int(response.headers.get('Retry-After', 1))
            logging.warning(f'Rate limit exceeded. Retrying after {retry_after} seconds.')
            time.sleep(retry_after)
        else:
            return response