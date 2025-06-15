import uuid
import os
import logging

from confluent_kafka import SerializingProducer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


KAFKA_BROKER = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")
TOPIC = os.getenv("TOPIC", "transaction")
NUM_MESSAGES = int(os.getenv("NUM_MESSAGES", "100"))
NUM_PARTITIONS = int(os.getenv("NUM_PARTITIONS", "1"))
REPLICATION_FACTOR = int(os.getenv("REPLICATION_FACTOR", "1"))

# Avro schema with primitive types
avro_schema_str = """
{
  "type": "record",
  "name": "Transaction",
  "fields": [
    { "name": "null_field",    "type": "null" },
    { "name": "boolean_field", "type": "boolean" },
    { "name": "int_field",     "type": "int" },
    { "name": "long_field",    "type": "long" },
    { "name": "float_field",   "type": "float" },
    { "name": "double_field",  "type": "double" },
    { "name": "bytes_field",   "type": "bytes" },
    { "name": "string_field",  "type": "string" }
  ]
}
"""

def to_dict(obj, ctx):
    return obj

def create_producer():
    schema_registry_conf = {'url': SCHEMA_REGISTRY_URL}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    avro_serializer = AvroSerializer(schema_registry_client, avro_schema_str, to_dict)

    producer_conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'key.serializer': StringSerializer('utf_8'),
        'value.serializer': avro_serializer
    }

    return SerializingProducer(producer_conf)

def create_topic_if_needed():
    admin_client = AdminClient({'bootstrap.servers': KAFKA_BROKER})
    metadata = admin_client.list_topics(timeout=5)
    
    if TOPIC in metadata.topics:
        logger.info(f"Topic '{TOPIC}' already exists.")
        return None 

    topic = NewTopic(
        TOPIC,
        num_partitions=NUM_PARTITIONS,
        replication_factor=REPLICATION_FACTOR
    )

    logger.info(f"Creating topic '{TOPIC}'...")
    futures = admin_client.create_topics([topic])

    for topic_name, future in futures.items():
        try:
            future.result()
            logger.info(f"Topic '{topic_name}' created successfully.")
        except Exception as e:
            logger.error(f"Failed to create topic '{topic_name}': {e}")

def send_messages(n):
    producer = create_producer()

    for i in range(1, n + 1):
        message = {
            "null_field": None,
            "boolean_field": (i % 2 == 0),
            "int_field": i,
            "long_field": i * 10000000000,
            "float_field": float(i) + 0.1,
            "double_field": float(i) * 2.718,
            "bytes_field": f"data-{i}".encode("utf-8"),
            "string_field": f"Primitive message {i}"
        }

        logger.info(f"Sending message: {message}")
        producer.produce(topic=TOPIC, key=str(i), value=message)
        producer.flush()

    logger.info("All primitive Avro messages sent.")

if __name__ == '__main__':
    logger.info(f"Preparing to send {NUM_MESSAGES} Avro messages to topic '{TOPIC}'...")
    create_topic_if_needed()
    send_messages(NUM_MESSAGES)
