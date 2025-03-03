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


class TMDBClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def request_movie_id(self, movie_name, movie_year=None):
        url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": self.api_key, "query": movie_name}
        response = requests.get(url, params=params)
        data = response.json()
        ret = None
        if data:
            for movie in data["results"]:
                if fuzz.ratio(movie_name, movie["original_title"]) > 90 and (
                    movie["release_date"][:4] == movie_year or not movie_year
                ):
                    ret = movie["id"]
                    break
        return ret

    def request_similar_movies(self, movie_id):
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations"
        params = {"api_key": self.api_key}
        response = requests.get(url, params=params)
        data = response.json()
        ret_list = []

        for movie in data["results"]:
            if (
                movie.get("vote_average", 0) >= self.minimum_rating
                and movie.get("vote_count", 0) >= self.minimum_votes
            ):
                if (
                    movie.get("original_language", "en") == self.language_choice
                    or self.language_choice == "all"
                ):
                    ret_list.append(movie)

        return ret_list
