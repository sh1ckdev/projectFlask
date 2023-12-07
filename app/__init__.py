from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_login import LoginManager
import os

app = Flask(__name__)
secret_key = os.urandom(24)
app.secret_key = secret_key
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:8000"}})
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
login_manager = LoginManager(app)

from app import routes
