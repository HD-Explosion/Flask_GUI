#!/usr/bin/python
import sys
import logging
import os
from dotenv import load_dotenv
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/app/")

load_dotenv()
secret_key = os.getenv('SECRET_KEY')
from app import app as application
#application.secret_key = 'Add your secret key'
application.secret_key = secret_key
