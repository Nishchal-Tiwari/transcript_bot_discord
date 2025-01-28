from kombu import Connection, Exchange, Producer

# Constants
REDIS_URL = "redis://localhost:6379/0"
EXCHANGE_NAME = "dm_exchange"
ROUTING_KEY = "dm_key"

# Setup the exchange
exchange = Exchange(EXCHANGE_NAME, type="direct")

def send_to_queue(user_id, message_content):
    """Send a message to the DM queue."""
    with Connection(REDIS_URL) as conn:
        producer = Producer(conn, exchange)
        producer.publish(
            {"id": str(user_id), "message": message_content},  # Ensure user_id is a string
            routing_key=ROUTING_KEY
        )
        print(f"Message sent to queue for user {user_id}")

if __name__ == "__main__":
    # Example usage
    user_id = 834348548106485761  # Replace with the target Discord user ID
    message_content = "Hello! This is a message from the producer."
    send_to_queue(user_id, message_content)
