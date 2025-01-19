import os
from openai import OpenAI
api_key = os.getenv("OPENAPI_KEY")
os.environ["OPENAI_API_KEY"] = api_key
client = OpenAI()


def transcribe_audio(audio_file_path, user_id):
    try:
        # Open the audio file
        with open(audio_file_path, "rb") as audio_file:
            # Request transcription
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json"
            )

        # Extract segments
        if hasattr(response, "segments"):
            return [
                {
                    "user_id": user_id,
                    "start": segment.start,  # Access attributes using dot notation
                    "end": segment.end,      # Access attributes using dot notation
                    "text": segment.text     # Access attributes using dot notation
                }
                for segment in response.segments
            ]
        else:
            print("No 'segments' attribute in the transcription response.")
            return []
    except Exception as e:
        print(f"Error while transcribing audio for user {user_id}: {e}")
        return []


def create_meeting_transcript(user_audio_files):
    unified_transcript = []

    for user_data in user_audio_files:
        user_id = user_data["user_id"]
        audio_file_path = user_data["audio_file_path"]
        user_transcription = transcribe_audio(audio_file_path, user_id)
        print(f"Transcription for {user_id}: {user_transcription}")
        unified_transcript.extend(user_transcription)

    # Sort transcript by start time
    unified_transcript.sort(key=lambda x: x["start"])
    return unified_transcript


def save_transcript_to_file(transcript, output_file_path):
    with open(output_file_path, "w") as file:
        for segment in transcript:
            file.write(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] ({segment['user_id']}): {segment['text']}\n")


# Example usage
user_audio_files = [
    {"user_id": "User1", "audio_file_path": "/Users/nishchaltiwari/dev/pvt/discord-voice-transcript-for-teams/recordings/general/recording_DeltaXPR_20250118_032620.wav"},
    {"user_id": "User3", "audio_file_path": "/Users/nishchaltiwari/dev/pvt/discord-voice-transcript-for-teams/recordings/general/recording_SmìLe_20250118_032620.wav"},
]

# Create the meeting transcript
# meeting_transcript = create_meeting_transcript(user_audio_files)

# # Save the transcript to a file
# output_file_path = "meeting_transcript.txt"
# save_transcript_to_file(meeting_transcript, output_file_path)
# print(f"Transcript saved to {output_file_path}")
