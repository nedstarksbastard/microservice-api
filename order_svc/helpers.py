import requests
import json
import sqlite3
import os
from datetime import datetime
from flask import current_app


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def get_product(code):
    try:
        print(f"{current_app.config['PRODUCT_URL']}/{code}")
        resp = requests.get(f"{current_app.config['PRODUCT_URL']}/{code}")
    except requests.exceptions.ConnectionError:
        raise InvalidUsage(f'Failed to connect to Product Service', 503)

    if resp.status_code == 200:
        d = resp.json()
        return d["name"], d["price"]
    else:
        raise InvalidUsage(f'Failed to load product with code - {code}', 500)


def get_user(uid):
    try:
        resp = requests.get(f"{current_app.config['USER_URL']}/{uid}")
    except requests.exceptions.ConnectionError:
        raise InvalidUsage(f'Failed to connect to User Service', 503)

    if resp.status_code == 200:
        d = resp.json()
        return f"{d['firstName']} {d['lastName']}"
    else:
        raise InvalidUsage(f'Could not find a user associated with id - {uid}', 404)


def add_order(user_id, user_name, product_code, product_name, price):
    # initialize db if it doesn't exist
    if not os.path.exists(current_app.config['DATABASE']):
        init_db()

    with sqlite3.connect(current_app.config['DATABASE']) as conn:
        c = conn.cursor()
        q = "INSERT INTO orders VALUES (NULL,?,?,?,?,?, datetime('now'))"
        c.execute(q, (user_id, user_name, product_code, product_name, price))
        conn.commit()
        return c.lastrowid


def get_orders(order_id=None):
    # initialize db if it doesn't exist
    if not os.path.exists(current_app.config['DATABASE']):
        init_db()

    with sqlite3.connect(current_app.config['DATABASE']) as conn:
        c = conn.cursor()

        if order_id:
            order_id = int(order_id)  # Ensure that we have a valid id value to query
            q = "SELECT * FROM orders WHERE id=? ORDER BY created_at DESC"
            rows = c.execute(q, (order_id,))

        else:
            q = "SELECT * FROM orders ORDER BY created_at DESC"
            rows = c.execute(q)

        return [{'id': r[0],
                 'user_id': r[1],
                 'customer_fullname': r[2],
                 'product_code': r[3],
                 'product_name': r[4],
                 'total_amount': r[5],
                 'created_at': r[6]} for r in rows]


def create_message(order_id):

    order = get_orders(order_id)[0]
    d = {"producer": "add_order",
         "sent_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
         "type": "order_ack",
         "payload": {
             "order": {
                 "order_id": str(order['id']),
                 "customer_fullname": order['customer_fullname'],
                 "product_name": order['product_name'],
                 "total_amount": order['total_amount'],
                 "created_at": order['created_at']
             }
         }
         }
    return json.dumps(d)


def init_db():
    try:
        conn = sqlite3.connect(current_app.config['DATABASE'])
        # Absolute path needed for testing environment
        sql_path = os.path.join(current_app.config['APP_ROOT'], 'db_init.sql')
        with open(sql_path, 'r') as f:
            cmd = f.read()
        crsr = conn.cursor()
        crsr.execute(cmd)
        conn.commit()
        conn.close()
    except IOError:
        print("Couldn't initialize the database, exiting...")
        raise
    except sqlite3.OperationalError:
        print("Couldn't execute the SQL, exiting...")
        raise


