import whisper
import os
import json
import logging
from src.tools.audioTool import split_audio_file_time, reencode_audio

class WhisperTranscriber:
    def __init__(self, model_name="base"):
        """
        Initialize the WhisperTranscriber class by loading the Whisper model.

        Args:
            model_name (str): Name of the Whisper model to load.
        """
        try:
            self.model = whisper.load_model(model_name)
            logging.info(f"Whisper model '{model_name}' loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading Whisper model '{model_name}': {e}")
            raise
    def sort_transcriptions(self, transcriptions):
        """
        Sort transcriptions by their start time.
        Args:
            transcriptions (list): List of transcription segments.
            """
        return sorted(transcriptions, key=lambda x: (x['start'], x['end']))
    def transcription_to_str(self, transcription):
        """
        Convert transcription segments to a single string.
        Args: 
        transcription (list): List of transcription segments.
        """
        
        combined_transcription = ""
        for segment in transcription:
            combined_transcription += f"{segment["user_id"]} [ {segment["start"]} {segment["end"]} ] {segment["text"]}\n"
        return combined_transcription
    def get_txt_only(self, transcription):
        """
        Extract text only from transcription segments.
        Args:
            transcription (list): List of transcription segments.
        """
        combined_transcription = ""
        for segment in transcription:
            combined_transcription += f"{segment["text"]} "
        return combined_transcription

    def transcribe_audio_chunk(self, audio_chunk_path, user_id, chunk_offset):
        """
        Transcribe a single audio chunk.

        Args:
            audio_chunk_path (str): Path to the audio chunk.
            user_id (str): User ID for reference.
            chunk_offset (int): Time offset for the chunk.

        Returns:
            list: Transcription segments with timestamps.
        """
        try:
            result = self.model.transcribe(audio_chunk_path, verbose=False)
            if "segments" in result:
                return [
                    {
                        "user_id": user_id,
                        "start": segment["start"] + chunk_offset,
                        "end": segment["end"] + chunk_offset,
                        "text": segment["text"],
                    }
                    for segment in result["segments"]
                ]
            return []
        except Exception as e:
            logging.error(f"Error while transcribing chunk {audio_chunk_path}: {e}")
            return []

    def transcribe_large_audio_file(self, audio_file_path, user_id, chunk_duration=300):
        """
        Transcribe a large audio file by splitting it into smaller chunks.

        Args:
            audio_file_path (str): Path to the audio file.
            user_id (str): User ID for reference.
            chunk_duration (int): Duration of each chunk in seconds.

        Returns:
            list: Complete transcription data.
        """
        try:
            re_path = reencode_audio(audio_file_path)
            chunks = split_audio_file_time(re_path, chunk_duration=chunk_duration)

            all_segments = []
            for i, chunk_file in enumerate(chunks):
                chunk_offset = i * chunk_duration
                segments = self.transcribe_audio_chunk(chunk_file, user_id, chunk_offset)
                all_segments.extend(segments)
                os.remove(chunk_file)  # Clean up

            return all_segments
        except Exception as e:
            logging.error(f"Error processing file {audio_file_path}: {e}")
            return []

# # Example usage
# if __name__ == "__main__":
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s [%(levelname)s]: %(message)s",
#     )

#     audio_path = "/Users/nishchaltiwari/dev/pvt/zerve2/testing/recording_Musico_20250127_163207.wav"
#     user_id = "example_user"
    
#     try:
#         transcriber = WhisperTranscriber()
#         result = transcriber.transcribe_large_audio_file(audio_path, user_id)
#         output_file = "transcription_results.json"
#         with open(output_file, "w") as f:
#             json.dump(result, f, indent=4)
#         logging.info(f"Transcription saved to {output_file}")
#     except Exception as e:
#         logging.error(f"Failed to transcribe audio: {e}")
