import os
import requests
import logging
from dotenv import load_dotenv
from time import sleep

# Load environment variables
load_dotenv()

# Salad API setup
SALAD_API_URL = 'https://api.salad.com/api/public/organizations/mmmcom/inference-endpoints/transcribe/jobs'
SALAD_API_KEY = 'cbc134c9-2fae-4b59-ad4f-d3c18ab49379'

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def transcribe_audio_with_salad(file_path):

    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return {"error": "File not found"}

    # Prepare headers and file data for the request
    headers = {
        'Content-Type': 'application/json',
        'Salad-Api-Key': SALAD_API_KEY
    }
    
    # File upload logic (if the API supports direct file uploads)
    try:
        # Send transcription request
        data = {
            "input": {
                "url": "https://jsw.backend-testing.store/abc.wav",
                "language_code": "en",
                "word_level_timestamps": False,
                "diarization": False,
                "srt": False
            }
        }

        response = requests.post(SALAD_API_URL, headers=headers, json=data)
        if response.status_code not in [200, 201]:
            logging.error(f"Failed to start transcription: {response.text}")
            return {"error": "Failed to start transcription"}

        job_id = response.json().get('id')
        logging.info(f"Transcription job started with ID: {job_id}")

        # Polling for the transcription result
        while True:
            status_response = requests.get(f"{SALAD_API_URL}/{job_id}", headers=headers)
            if status_response.status_code != 200:
                logging.error(f"Failed to fetch job status: {status_response.text}")
                return {"error": "Failed to fetch job status"}

            status_data = status_response.json()
            status = status_data.get('status')

            if status == 'succeeded':
                logging.info("Transcription completed successfully.")
                return status_data
            elif status == 'failed':
                logging.error("Transcription failed.")
                return {"error": "Transcription failed"}
            
            logging.info("Transcription in progress. Retrying in 30 seconds...")
            sleep(30)

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {str(e)}")
        return {"error": str(e)}


# Replace with the path to your audio file
audio_file_path = "recordings/general/recording_SmìLe_20250118_032620.wav"

# Transcribe the audio
transcription_result = transcribe_audio_with_salad(audio_file_path)

# Check and print the transcription result
if "error" in transcription_result:
    print(f"Error: {transcription_result['error']}")
else:
    print("Transcription result:", transcription_result)
