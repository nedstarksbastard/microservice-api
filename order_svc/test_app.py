import unittest
import app
import tempfile
import os
import json
from unittest.mock import patch
from helpers import add_order


class OrderServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app.app.test_client()
        db_fd, cls.app.application.config['DATABASE'] = tempfile.mkstemp()
        cls.app.application.config['TESTING'] = True
        cls.app.application.config['PUBLISH'] = False
        cls.app.application.config['SUBSCRIBE'] = False
        os.close(db_fd)
        os.unlink(cls.app.application.config['DATABASE'])
        print("setUpClass")

    def test_home_status_code(self):
        result = self.app.get('/')
        # assert the status code of the response
        self.assertEqual(result.status_code, 200)

    def test_home_data(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/')

        # assert the response data
        self.assertEqual(result.data.decode('utf-8'), "Order Service")

    @patch('helpers.get_user')
    @patch('helpers.get_product')
    def test_add_order(self, mocked_get_user, mocked_get_product):
        mocked_get_user.return_value = "Fizi Yadav"
        user = mocked_get_user()
        self.assertEqual(user, "Fizi Yadav")
        mocked_get_product.return_value = ("Paleo Box", 10.0)
        product, price = mocked_get_product()

        with self.app.application.app_context():
            order_id = add_order("xyz123", user, "paleo-box", product, price)
        self.assertEqual(order_id, 1)

    def test_order_saved(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/all_orders')
        order = json.loads(result.data)[0]

        # assert the response data
        self.assertEqual(order["id"], 1)
        self.assertEqual(order["product_code"], "paleo-box")
        self.assertEqual(order["customer_fullname"], "Fizi Yadav")


    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.app.application.config['DATABASE']):
            os.remove(cls.app.application.config['DATABASE'])
        print("tearDownClass")


if __name__ == "__main__":
    unittest.main()