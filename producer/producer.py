import json
import logging
import os
import time

from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
from confluent_kafka.admin import AdminClient, NewTopic


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

TOPIC_NAME = os.getenv('TOPIC_NAME', 'transactions')
BOOTSTRAP_SERVERS = os.getenv('BOOTSTRAP_SERVERS')
SCHEMA_REGISTRY_URL = os.getenv('SCHEMA_REGISTRY_URL')  



admin_client = AdminClient({"bootstrap.servers": BOOTSTRAP_SERVERS})
topic = NewTopic(TOPIC_NAME, num_partitions=1, replication_factor=1)


# Create Kafka Topic
admin_client.create_topics([topic])

kafka_props = {    
    'bootstrap.servers': BOOTSTRAP_SERVERS,
    'schema.registry.url': SCHEMA_REGISTRY_URL} 

topic_schema = avro.load('transactions.avsc')


producer = AvroProducer(
    config=kafka_props,
    default_value_schema=topic_schema
)

with open('transactions.json', 'r') as file:
    transactions = json.load(file)

for tx in transactions:
    producer.produce(topic=TOPIC_NAME, value=tx)
    logger.info(f'Enviado: {tx}')
    time.sleep(0.5)

producer.flush()
