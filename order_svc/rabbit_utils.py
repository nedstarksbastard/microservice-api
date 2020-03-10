import pika
import time


class OrderPublisher:

    def __init__(self, host, cred, exchange):
        self.host = host
        self.cred = cred
        self.connection = None
        self.channel = None
        self.exchange = exchange

    def connect(self, retries=1):
        for i in range(retries):
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.host, credentials=self.cred))
                break
            except pika.exceptions.AMQPConnectionError:
                print(f"Could not connect to rabbitmq host. Retries left {retries-i-1}")
                time.sleep(5)

        if self.connection:
            print(f"Connected to rabbitmq host")
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange=self.exchange, exchange_type='fanout')
        else:
            print(f"Could not connect to rabbitmq host.")

    def call(self, msg):
        try:
            self.channel.basic_publish(
                exchange='orders',
                routing_key='created_order',
                body=msg)
            print(f"Published to exchange - {msg}")
        except pika.exceptions.StreamLostError:
            print("Lost connection to rabbitmq.")
            self.connection = None


class OrderReceiver:

    def __init__(self, host, cred, exchange, qname):
        self.host = host
        self.cred = cred
        self.exchange = exchange
        self.qname = qname
        self.connection = None
        self.channel = None
        self.callback_queue = None

    def connect(self, retries=1):
        for i in range(retries):
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.host, credentials=self.cred))
                break
            except pika.exceptions.AMQPConnectionError:
                print(f"Could not subscribe to rabbitmq host. Retries left {retries-i-1}")
                time.sleep(5)
        if self.connection:
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange=self.exchange, exchange_type='fanout')

            result = self.channel.queue_declare(self.qname, exclusive=False)
            self.callback_queue = result.method.queue

            self.channel.queue_bind(exchange=self.exchange, queue=self.callback_queue)
        else:
            print(f"Could not connect to rabbitmq host")

    def start_consuming(self):
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)
        try:
            self.channel.start_consuming()
        except pika.exceptions.StreamLostError:
            print("Lost connection to rabbitmq.")
            self.connection = None

    @staticmethod
    def on_response(ch, method, props, body):
        print(body)



