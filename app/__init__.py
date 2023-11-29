from flask import Flask
import mongoengine as me
from app.api import api_bp


app = Flask(__name__)

me.connect("costs_db")
app.register_blueprint(api_bp, url_prefix="/api")
