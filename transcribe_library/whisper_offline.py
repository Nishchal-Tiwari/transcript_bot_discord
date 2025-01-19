import whisper

def transcribe_audio_local(audio_file_path, user_id, model):
    try:
        # Transcribe the audio file
        result = model.transcribe(audio_file_path, verbose=False)

        # Extract segments
        if "segments" in result:
            return [
                {
                    "user_id": user_id,
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"]
                }
                for segment in result["segments"]
            ]
        else:
            print("No 'segments' found in transcription result.")
            return []
    except Exception as e:
        print(f"Error while transcribing audio for user {user_id}: {e}")
        return []

def create_meeting_transcript_local(user_audio_files, model):
    unified_transcript = []

    for user_data in user_audio_files:
        user_id = user_data["user_id"]
        audio_file_path = user_data["audio_file_path"]
        user_transcription = transcribe_audio_local(audio_file_path, user_id, model)
        print(f"Transcription for {user_id}: {user_transcription}")
        unified_transcript.extend(user_transcription)

    # Sort transcript by start time
    unified_transcript.sort(key=lambda x: x["start"])
    return unified_transcript

def save_transcript_to_file(transcript, output_file_path):
    with open(output_file_path, "w") as file:
        for segment in transcript:
            file.write(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] ({segment['user_id']}): {segment['text']}\n")

# Load the Whisper model
model = whisper.load_model("medium")

# Example usage
user_audio_files = [
    {"user_id": "User1", "audio_file_path": "/Users/nishchaltiwari/dev/pvt/discord-voice-transcript-for-teams/recordings/general/recording_DeltaXPR_20250118_032620.wav"},
    {"user_id": "User3", "audio_file_path": "/Users/nishchaltiwari/dev/pvt/discord-voice-transcript-for-teams/recordings/general/recording_SmìLe_20250118_032620.wav"},
]

# Create the meeting transcript using the local Whisper model
meeting_transcript = create_meeting_transcript_local(user_audio_files, model)

# Save the transcript to a file
output_file_path = "meeting_transcript_local.txt"
save_transcript_to_file(meeting_transcript, output_file_path)
print(f"Transcript saved to {output_file_path}")
