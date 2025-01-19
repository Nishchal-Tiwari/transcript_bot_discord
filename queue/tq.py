# tq.py
from rq import Queue
from redis import Redis
from tasks import add, subtract

# Connect to Redis
redis_conn = Redis()

# Create a queue
queue = Queue(connection=redis_conn)

# Enqueue tasks
job1 = queue.enqueue(add, 1, 2)
job2 = queue.enqueue(subtract, 10, 4)

print(f"Enqueued Job 1: {job1.id}")
print(f"Enqueued Job 2: {job2.id}")