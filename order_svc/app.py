from flask import Flask, make_response, jsonify, request
from settings import settings_dev, settings_prod
import threading

from helpers import InvalidUsage, get_user, get_product, add_order, create_message, get_orders
from rabbit_utils import OrderPublisher, OrderReceiver


app = Flask(__name__)
if app.config['ENV'] == "development":
    app.config.from_object(settings_dev)
else:
    app.config.from_object(settings_prod)

if app.config['PUBLISH']:
    order_publisher = OrderPublisher(app.config['RABBIT_MQ_HOST'], app.config['RABBIT_MQ_CRED'], 'orders')


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/')
def order_svc():
    return 'Order Service'


@app.route('/all_orders')
def get_all_orders():
    d = get_orders()
    return jsonify(d)


@app.route('/subscribe')
def subscribe_queue():
    # receive the messages published to RabbitMQ
    is_subscribed = app.config.get('SUBSCRIBE', None)
    if not is_subscribed:
        order_receiver = OrderReceiver(app.config['RABBIT_MQ_HOST'], app.config['RABBIT_MQ_CRED'], 'orders',
                                       'order_queue')
        order_receiver.connect()
        if order_receiver.connection:
            app.config['SUBSCRIBE'] = True
            threading.Thread(target=order_receiver.start_consuming).start()
            return make_response(jsonify({'success': True}), 200)
        else:
            raise InvalidUsage(f'Failed to subscribe to RabbitMQ', 503)
    else:
        return make_response(jsonify({'success': True}), 200)


@app.route('/orders', methods=['POST'])
def new_order():
    user_id = request.values['user_id']
    product_code = request.values['product_code']  # if key doesn't exist, returns a 400, bad request error

    if product_code:
        product_name, price = get_product(product_code)

    if user_id:
        user_name = get_user(user_id)

    order_id = add_order(user_id, user_name, product_code, product_name, price)

    if order_id:
        if app.config['PUBLISH']:
            if not order_publisher.connection:
                order_publisher.connect()

            msg = create_message(order_id)
            threading.Thread(target=order_publisher.call, args=(msg,)).start()

        return make_response(jsonify({'success': True}), 200)
    else:
        return InvalidUsage(f'Failed to store in DB - {product_code}', 500)


if __name__ == '__main__':
    app.run()
