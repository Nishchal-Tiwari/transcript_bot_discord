from kombu import Connection, Exchange, Queue
import time
from src.recordingProcessors.recordingProcessor import processGroupRecording
import traceback

# The code to rewrite
redis_url = "redis://localhost:6379/0"

exchange = Exchange("example_exchange", type="direct")
queue = Queue("example_queue", exchange, routing_key="example_key")
MAX_RETRIES = 1
retry_map = {}
def consumer():
    with Connection(redis_url) as conn:
        queue.maybe_bind(conn)
        with conn.Consumer(queue, callbacks=[process_message]) as consumer:
            while True:
                conn.drain_events()

def process_message(body, message):
    delivery_tag = message.delivery_tag
    try:
        print(f"Received[ W1 ]: {body}")
        processGroupRecording(body['message'])
        # time.sleep(40)
        message.ack()
    except Exception as e:
        retry_map[delivery_tag] = retry_map.get(delivery_tag, 0) + 1
        retries = retry_map[delivery_tag]
        if retries < MAX_RETRIES:
            # Requeue the message with updated headers
            message.requeue()
            print(f"Error processing message: {e}")
            traceback.print_exc()
            print(f"Message requeued (Attempt {retries})")
        else:
            # Log failure and discard message
            print(f"Error processing message: {e}")
            traceback.print_exc()
            print(f"Message discarded after {MAX_RETRIES} attempts")
            message.ack()
# Message processing function with retry logic

consumer()