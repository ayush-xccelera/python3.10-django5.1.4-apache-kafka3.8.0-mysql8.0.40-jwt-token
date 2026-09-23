"""Lightweight Kafka producer for publishing STOCK_UPDATED domain events.

Uses kafka-python. Failures to publish (e.g. broker not reachable in a local
dev/test environment) are logged but never break the HTTP request/response
cycle - the DB write is the source of truth and already committed by the
time we attempt to publish.
"""
import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

_producer = None


def _get_producer():
    global _producer
    if _producer is None:
        from kafka import KafkaProducer

        _producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=3,
        )
    return _producer


def publish_stock_updated(product_id, previous_quantity, new_quantity, timestamp):
    event = {
        'event': 'STOCK_UPDATED',
        'product_id': product_id,
        'previous_stock_quantity': previous_quantity,
        'new_stock_quantity': new_quantity,
        'timestamp': timestamp,
    }
    try:
        producer = _get_producer()
        producer.send(settings.KAFKA_STOCK_UPDATED_TOPIC, value=event)
        producer.flush(timeout=5)
    except Exception as exc:  # noqa: BLE001
        logger.warning('Failed to publish STOCK_UPDATED event: %s', exc)
    return event
