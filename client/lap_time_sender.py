import json
import os
import re
from json.decoder import JSONDecodeError

import requests
import time

from game_state import GameState


class LapTimeSender:
    def __init__(self, server: str):
        self.server = server
        self.__send_cached_lap_times()

    def send_lap_time(self, game_state: GameState):
        data = {
            'date': round(time.time()),
            'driver': game_state.driver,
            'track': game_state.track.to_json(),
            'car': game_state.car.to_json(),
            'time': game_state.last_lap_time,
            'session_type': 'race' if len(game_state.participants or []) > 1 else 'time-trial'
        }

        if True:  # game_state.has_player_data and game_state.has_telemetry_data:
            print("Sending laptime")

            if self.__post_lap_time(data):
                self.__send_cached_lap_times()
            else:
                self.__cache_lap_time(data)
        else:
            print("Game state incomplete, caching laptime")
            self.__cache_lap_time(data)

    @staticmethod
    def __cache_lap_time(data):
        file_name = "laptime_{}.json".format(data["date"])

        file = open(file_name, "w")
        file.write(json.dumps(data))
        file.close()

    def __send_cached_lap_times(self):
        all_cache_files = list(filter(lambda f: bool(re.match(r"laptime_.*?\.json", f)), os.listdir('.')))

        for file in all_cache_files:
            file_content = open(file, "r").read()
            try:
                data = json.loads(file_content)
            except JSONDecodeError:
                # File is corrupt
                os.remove(file)
                continue

            if self.__post_lap_time(data):
                os.remove(file)

    def __post_lap_time(self, data):
        try:
            response = requests.post(
                '{}/laptime/submit'.format(self.server),
                data=json.dumps(data),
                headers={
                    "Content-Type": "application/json"
                }
            )
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
