import os
import subprocess
from pydub import AudioSegment




def reencode_audio(input_path, output_path):
    """Re-encode audio to mono and 16 kHz using ffmpeg."""
    try:
        subprocess.run(
            ["ffmpeg", "-i", input_path, "-ac", "1",
                "-ar", "16000", output_path, "-y"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"Re-encoded file saved as: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error during re-encoding: {e.stderr.decode()}")
        return None


def split_audio_file(audio_file_path, max_size_mb=10):
    """Split audio file into chunks of approximately max_size_mb."""
    audio = AudioSegment.from_file(audio_file_path)
    file_size_bytes = os.path.getsize(audio_file_path)

    # Calculate chunk size in milliseconds
    max_size_bytes = max_size_mb * 1024 * 1024
    duration_ms = len(audio)
    size_per_ms = file_size_bytes / duration_ms
    chunk_length_ms = int(max_size_bytes / size_per_ms)

    # Split the audio
    chunks = [audio[i:i + chunk_length_ms]
              for i in range(0, duration_ms, chunk_length_ms)]
    chunk_files = []
    for i, chunk in enumerate(chunks):
        chunk_file_path = f"{audio_file_path}_chunk_{i}.wav"
        chunk.export(chunk_file_path, format="wav")
        chunk_files.append(chunk_file_path)

    return chunk_files


def transcribe_audio(audio_file_path, user_id):
    """Transcribe audio using OpenAI Whisper API."""
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json"
            )
            print(response)

        # Process transcription response
        if hasattr(response, "segments"):
            return [
                {
                    "user_id": user_id,
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"]
                }
                for segment in response.segments
            ]
        else:
            print("No 'segments' attribute in the transcription response.")
            return []
    except Exception as e:
        print(f"Error while transcribing audio for user {user_id}: {e}")
        return []


def create_meeting_transcript(filepath, userid):
    """Create a unified transcript for multiple users."""
    unified_transcript = []
    user_id = userid
    audio_file_path = filepath

    # Re-encode the audio to ensure compatibility
    reencoded_path = f"{os.path.splitext(audio_file_path)[0]}_reencoded.wav"
    reencode_audio(audio_file_path, reencoded_path)

    # Check the size of the re-encoded file
    reencoded_file_size_mb = os.path.getsize(
        reencoded_path) / (1024 * 1024)
    print(f"Re-encoded file size: {reencoded_file_size_mb:.2f} MB")

    if reencoded_file_size_mb > 10:
        # Split the file into 10 MB chunks
        chunk_files = split_audio_file(reencoded_path, max_size_mb=10)
        print(f"File split into {len(chunk_files)} chunks.")
        for chunk_file in chunk_files:
            # Transcribe each chunk
            user_transcription = transcribe_audio(chunk_file, user_id)
            print(user_transcription)
            unified_transcript.extend(user_transcription)
            os.remove(chunk_file)  # Clean up chunk files
    else:
        # Transcribe the whole file
        user_transcription = transcribe_audio(reencoded_path, user_id)
        unified_transcript.extend(user_transcription)

    # Clean up the re-encoded file
    if os.path.exists(reencoded_path):
        os.remove(reencoded_path)
    print(unified_transcript)
    # Sort the transcript by start time
    unified_transcript.sort(key=lambda x: x["start"])
    return unified_transcript


def save_transcript_to_file(transcript, output_file_path):
    """Save the transcript to a text file."""
    with open(output_file_path, "w") as file:
        for segment in transcript:
            file.write(
                f"[{segment['start']:.2f}s - {segment['end']:.2f}s] ({segment['user_id']}): {segment['text']}\n"
            )


# # Example usage
# if __name__ == "__main__":
#     user_audio_files = [
#         {
#             "user_id": "User1",
#             "audio_file_path": "./recordings/general_20250123_193410/recording_DeltaXPR_20250123_193410.wav"
#         }
#     ]

#     # Create the meeting transcript
#     meeting_transcript = create_meeting_transcript(
#         user_audio_files[0]["audio_file_path"], user_audio_files[0]["user_id"])

#     # Save the transcript to a file
#     output_file_path = "meeting_transcript.txt"
#     save_transcript_to_file(meeting_transcript, output_file_path)
#     print(f"Transcript saved to {output_file_path}")
