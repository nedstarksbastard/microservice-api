"""Common settings are defined here. Only upper case variables are exported."""

import os
import pika

APP_ROOT = os.path.dirname(os.path.dirname(__file__))
DB_NAME = 'development.db'
DATABASE = os.path.join(APP_ROOT, DB_NAME)

SECRET_KEY = os.urandom(24)

PRODUCT_URL = "http://localhost:8081/products"
USER_URL = "http://localhost:8082/users"

RABBIT_MQ_HOST = "localhost"
RABBIT_MQ_CRED = pika.PlainCredentials('guest', 'guest')
PUBLISH = False
