from kombu import Connection, Exchange, Queue

# The code to rewrite
redis_url = "redis://localhost:6379/0"

exchange = Exchange("example_exchange", type="direct")
queue = Queue("example_queue", exchange, routing_key="example_key")

def producer():
    with Connection(redis_url) as conn:
        producer = conn.Producer(serializer="json")
        producer.publish(
            {"message": "/Users/nishchaltiwari/dev/pvt/zerve3/recordings/candace-project_20250129_011940/info.json"},
            exchange=exchange,
            routing_key="example_key",
            declare=[queue]
        )


producer()
