from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

UPLOAD_FOLDER = '/home/xiaohe/Documents/HD_Project/Flask_GUI/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from app import routes, models
