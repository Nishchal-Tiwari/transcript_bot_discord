from kombu import Connection, Exchange, Queue
import discord
import asyncio
import traceback
from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()

# Constants
REDIS_URL = "redis://localhost:6379/0"
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
EXCHANGE_NAME = "dm_exchange"
QUEUE_NAME = "dm_queue"
ROUTING_KEY = "dm_key"

# Kombu Exchange and Queue
exchange = Exchange(EXCHANGE_NAME, type="direct")
queue = Queue(QUEUE_NAME, exchange, routing_key=ROUTING_KEY)

# Discord DM class
class DiscordDMWorker:
    def __init__(self, token):
        self.token = token
        self.client = discord.Client(intents=discord.Intents.default())
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.client.start(self.token))
        self.loop.run_until_complete(self.wait_until_ready())

    async def wait_until_ready(self):
        """Wait until the Discord bot is ready."""
        await self.client.wait_until_ready()
        print(f"Discord bot logged in as {self.client.user}")

    async def send_dm(self, user_id, message_content):
        """Send a DM to the specified user."""
        try:
            user = await self.client.fetch_user(user_id)
            await user.send(message_content)
            print(f"DM sent to user {user_id}")
        except Exception as e:
            print(f"Failed to send DM to {user_id}: {e}")
            traceback.print_exc()
    async def send_dm_in_chunk(self, user_id, message_content):
        """Send a DM to the specified user in chunks if necessary."""
        try:
            # Fetch the user
            user = await self.client.fetch_user(user_id)

            # Maximum chunk size (Discord limit is 2000, we use 1500 for safety)
            max_chunk_size = 1500

            # Split the message into chunks
            chunks = [message_content[i:i + max_chunk_size] for i in range(0, len(message_content), max_chunk_size)]

            # Send each chunk separately
            for i, chunk in enumerate(chunks, 1):
                await user.send(chunk)
                print(f"Chunk {i}/{len(chunks)} sent to user {user_id}")

        except Exception as e:
            print(f"Failed to send DM to {user_id}: {e}")
            traceback.print_exc()

    def send_message(self, user_id, message_content):
        """Wrapper for sending a DM."""
        self.loop.run_until_complete(self.send_dm_in_chunk(user_id, message_content))


# Worker function
def start_worker():
    """Start the worker to consume messages and send DMs."""
    dm_worker = DiscordDMWorker(DISCORD_TOKEN)

    def process_message(body, message):
        try:
            user_id = body.get("id")
            dm_message = body.get("message")

            if not user_id or not dm_message:
                raise ValueError("Message must contain 'id' and 'message' fields")

            # Send the DM
            dm_worker.send_message(int(user_id), dm_message)

            # Acknowledge the message
            message.ack()
        except Exception as e:
            print(f"Error processing message: {e}")
            traceback.print_exc()
            message.reject()

    # Kombu connection and consumer setup
    with Connection(REDIS_URL) as connection:
        queue.maybe_bind(connection)
        with connection.Consumer(queue, callbacks=[process_message]):
            print("Worker started. Listening for DM messages...")
            while True:
                try:
                    connection.drain_events(timeout=2)
                except KeyboardInterrupt:
                    print("Worker stopped.")
                    break
                except ConnectionError as e:
                    print(f"Connection error: {e}")
                    traceback.print_exc()
                    break
                except asyncio.TimeoutError:
                    # Timeout when no events are received, continue listening
                    continue
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    traceback.print_exc()


if __name__ == "__main__":
    start_worker()
