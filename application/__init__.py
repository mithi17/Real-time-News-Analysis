from flask import Flask, render_template,request, redirect, url_for, jsonify
import requests
from flask_pymongo import PyMongo
from datetime import datetime
from bs4 import BeautifulSoup
import re


app = Flask(__name__)
# app.config["SECRET_KEY"] = "0b843bd82ddf4e8fe85e93a77e29e1b73561c06a"
# app.config["MONGO_URI"] = "mongodb://localhost:27017/FlaskApp"

mongo = PyMongo(app,uri="mongodb://localhost:27017/database")
db = mongo.db

from application import routes


