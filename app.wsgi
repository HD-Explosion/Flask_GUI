#!/usr/bin/python
import sys
import logging
import os
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/app/")

from app import app as application
#application.secret_key = 'Add your secret key'
application.secret_key = 'b\x12\x05@\xdc\xf2e9\xb3\x9a%\xab\x11\x02\\+\xe8\xc5k\x8f\xbe\xe1Sa\xe8\xb5\x03f'

