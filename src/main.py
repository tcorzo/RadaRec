from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
from data_handler import DataHandler

class App:
    def __init__(self, host="0.0.0.0", port=5000, secret_key="secret_key"):
        self.app = Flask(__name__)
        self.app.secret_key = secret_key
        self.socketio = SocketIO(self.app)
        self.data_handler = DataHandler(self.socketio)
        self.host = host
        self.port = port

        self.register_routes()

    def register_routes(self):
        @self.app.route("/")
        def home():
            return render_template("base.html")

        @self.socketio.on("side_bar_opened")
        def side_bar_opened():
            if self.data_handler.radarr_items:
                ret = {
                    "Status": "Success",
                    "Data": self.data_handler.radarr_items,
                    "Running": not self.data_handler.stop_event.is_set()
                }
                self.socketio.emit("radarr_sidebar_update", ret)

        @self.socketio.on("get_radarr_movies")
        def get_radarr_movies():
            thread = threading.Thread(
                target=self.data_handler.request_movies_from_radarr,
                name="Radarr_Thread"
            )
            thread.daemon = True
            thread.start()

        @self.socketio.on("adder")
        def add_movies(data):
            thread = threading.Thread(
                target=self.data_handler.add_movies,
                args=(data,),
                name="Add_Movies_Thread"
            )
            thread.daemon = True
            thread.start()

        @self.socketio.on("connect")
        def connection():
            self.data_handler.connection()

        @self.socketio.on("disconnect")
        def disconnection():
            self.data_handler.disconnection()

        @self.socketio.on("load_settings")
        def load_settings():
            self.data_handler.load_settings()

        @self.socketio.on("update_settings")
        def update_settings(data):
            self.data_handler.update_settings(data)
            self.data_handler.save_config_to_file()

        @self.socketio.on("start_req")
        def starter(data):
            self.data_handler.start(data)

        @self.socketio.on("stop_req")
        def stopper():
            self.data_handler.stop_event.set()

        @self.socketio.on("load_more_movies")
        def load_more_movies():
            thread = threading.Thread(
                target=self.data_handler.find_similar_movies,
                name="Find_Similar"
            )
            thread.daemon = True
            thread.start()

    def run(self):
        self.socketio.run(self.app, host=self.host, port=self.port)


if __name__ == "__main__":
    app_instance = App()
    app_instance.run()
