from flask import *
from datetime import timedelta
from flask.helpers import flash
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send
from werkzeug.utils import secure_filename
import subprocess
import os
import requests