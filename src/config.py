import json
import time
import logging
import os
import random
from flask_socketio import SocketIO
import threading
import urllib.parse
import requests
from unidecode import unidecode
from iso639 import Lang
from dataclasses import dataclass


@dataclass
class ConfigContent:
    radarr_address: str
    radarr_api_key: str
    root_folder_path: str
    tmdb_api_key: str

class Config:
    config = {}

    def __init__(self, socketio):
        self.socketio = socketio
        self.load_config()

    def load(self):
        try:
            data = {
                "radarr_address": self.radarr_client.url,
                "radarr_api_key": self.radarr_client.api_key,
                "root_folder_path": self.root_folder_path,
                "tmdb_api_key": self.tmdb_client.api_key,
            }
            self.socketio.emit("settings_loaded", data)
        except Exception as e:
            self.radarec_logger.error(f"Failed to load settings: {str(e)}")

    def update(self, data):
        try:
            self.radarr_address = data["radarr_address"]
            self.radarr_api_key = data["radarr_api_key"]
            self.tmdb_api_key = data["tmdb_api_key"]
            self.root_folder_path = data["root_folder_path"]
        except Exception as e:
            self.radarec_logger.error(f"Failed to update settings: {str(e)}")

    def save_config_to_file(self):
        try:
            with open(self.settings_config_file, "w") as json_file:
                json.dump(
                    {
                        "radarr_address": self.radarr_address,
                        "radarr_api_key": self.radarr_api_key,
                        "root_folder_path": self.root_folder_path,
                        "tmdb_api_key": self.tmdb_api_key,
                        "fallback_to_top_result": self.fallback_to_top_result,
                        "radarr_api_timeout": float(self.radarr_api_timeout),
                        "quality_profile_id": self.quality_profile_id,
                        "metadata_profile_id": self.metadata_profile_id,
                        "search_for_movie": self.search_for_movie,
                        "dry_run_adding_to_radarr": self.dry_run_adding_to_radarr,
                        "minimum_rating": self.minimum_rating,
                        "minimum_votes": self.minimum_votes,
                        "language_choice": self.language_choice,
                        "auto_start": self.auto_start,
                        "auto_start_delay": self.auto_start_delay,
                    },
                    json_file,
                    indent=4,
                )

        except Exception as e:
            self.radarec_logger.error(f"Error Saving Config: {str(e)}")
