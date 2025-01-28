import json
import time
import os
from kombu import Connection, Exchange, Producer
from src.transcribers.whispher_transcriber import WhisperTranscriber
from src.summarizers.gemini_summarizer import GeminiSummarizer
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

transcriber = WhisperTranscriber()
summarizer = GeminiSummarizer()
# Exchange and Queue for Discord DM
DM_EXCHANGE_NAME = "dm_exchange"
DM_ROUTING_KEY = "dm_key"
REDIS_URL = os.getenv('REDIS_URL')#"redis://localhost:6379/0"
dm_exchange = Exchange(DM_EXCHANGE_NAME, type="direct")

def send_to_queue(user_id, message_content):
    """Send a message to the DM queue."""
    with Connection(REDIS_URL) as conn:
        producer = Producer(conn, dm_exchange)
        producer.publish(
            {"id": str(user_id), "message": message_content},  # Ensure user_id is a string
            routing_key=DM_ROUTING_KEY
        )
        print(f"Message sent to queue for user {user_id}")
def processRawJson(filePath):
    if not os.path.exists(filePath):
        raise FileNotFoundError(f"No such file: '{filePath}'")
    with open(filePath, 'r') as f:
        data = json.load(f)
    return data
def saveJson(data, filePath):
    with open(filePath, 'w') as f:
        json.dump(data, f, indent=4)
    
def processGroupRecording(filePath):
    info = processRawJson(filePath)
    users = info['users']
    transcriptions = []
    for data in users:
        file_path = data['file_path']
        userName = data['user_name']
        transcription = transcriber.transcribe_large_audio_file(file_path,userName)
        transcriptions.extend(transcription)
    transcriptions = transcriber.sort_transcriptions(transcriptions)
    summary = summarizer.get_summary(transcriber.transcription_to_str(transcriptions))
    for data in users:
        send_to_queue(data['user_id'],transcriber.transcription_to_str(transcriptions))
        send_to_queue(data['user_id'],json.dumps(summary["important_points"]))
        send_to_queue(data['user_id'],json.dumps(summary["tasks"]))
        send_to_queue(data['user_id'],json.dumps(summary["summary"]))
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_dir = f'output/{timestamp}'
    os.makedirs(output_dir, exist_ok=True)
    saveJson(summary, os.path.join(output_dir, 'summary.json'))
    saveJson(transcriptions, os.path.join(output_dir, 'transcriptions.json'))

    

if __name__ == '__main__':
    file_path = '/Users/nishchaltiwari/dev/pvt/zerve2/recordings/announcements_20250126_004014/info.json'
    processGroupRecording(file_path)
