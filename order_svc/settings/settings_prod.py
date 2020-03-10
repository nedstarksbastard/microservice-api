"""Common settings are defined here. Only upper case variables are exported."""

import os
import pika


APP_ROOT = os.path.dirname(os.path.dirname(__file__))
DB_NAME = 'production.db'
DATABASE = os.path.join(APP_ROOT, DB_NAME)

SECRET_KEY = os.urandom(24)

PRODUCT_URL = "http://product-service:8080/products"
USER_URL = "http://user-service:8080/users"

RABBIT_MQ_HOST = "rabbitmq"
RABBIT_MQ_CRED = pika.PlainCredentials('hellofresh', 'food')
PUBLISH = True
