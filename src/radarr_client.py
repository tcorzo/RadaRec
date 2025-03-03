import json
import time
import logging
import os
import random
from flask_socketio import SocketIO
import threading
import urllib.parse
import requests
from thefuzz import fuzz
from unidecode import unidecode
import re
from iso639 import Lang

class RadarrClient:
    url = None
    api_key = None
    radarr_items = []

    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key

    def get_movies(self, checked=False):
        try:
            self.radarec_logger.info(f"Getting Movies from Radarr")
            endpoint = f"{self.url}/api/v3/movie"
            headers = {"X-Api-Key": self.api_key}
            response = requests.get(
                endpoint, headers=headers, timeout=self.radarr_api_timeout
            )

            if response.status_code == 200:
                self.full_radarr_movie_list = response.json()
                self.radarr_items = [
                    {
                        "name": re.sub(
                            r" \(\d{4}\)",
                            "",
                            unidecode(movie["title"], replace_str=" "),
                        ),
                        "checked": checked,
                    }
                    for movie in self.full_radarr_movie_list
                ]
                self.radarr_items.sort(key=lambda x: x["name"].lower())
                self.cleaned_radarr_items = [
                    item["name"].lower() for item in self.radarr_items
                ]
                status = "Success"
                data = self.radarr_items
            else:
                status = "Error"
                data = response.text

            ret = {
                "Status": status,
                "Code": response.status_code if status == "Error" else None,
                "Data": data,
                "Running": not self.stop_event.is_set(),
            }

        except Exception as e:
            self.radarec_logger.error(f"Getting Movie Error: {str(e)}")
            ret = {
                "Status": "Error",
                "Code": 500,
                "Data": str(e),
                "Running": not self.stop_event.is_set(),
            }

        finally:
            self.socketio.emit("radarr_sidebar_update", ret)
