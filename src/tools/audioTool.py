import os
import subprocess
from pydub import AudioSegment
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
)

def generate_output_path(input_path):
    """Generate a default output path based on the input path."""
    base, ext = os.path.splitext(input_path)
    return f"{base}_reencoded{ext}"

def reencode_audio(input_path, output_path=None):
    """
    Re-encode audio to mono and 16 kHz using ffmpeg.

    Args:
        input_path (str): Path to the input audio file.
        output_path (str): Path to save the re-encoded file.

    Returns:
        str: Path to the re-encoded file.
    """
    if not os.path.exists(input_path):
        logging.error(f"Input file does not exist: {input_path}")
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    output_path = output_path or generate_output_path(input_path)

    try:
        subprocess.run(
            ["ffmpeg", "-i", input_path, "-ac", "1", "-ar", "16000", output_path, "-y"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logging.info(f"Re-encoded file saved as: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during re-encoding: {e.stderr.decode()}")
        raise

def split_audio_file_time(audio_file_path, chunk_duration=300, output_dir="chunks", overlap=0):
    """
    Split an audio file into smaller chunks of a specified duration.

    Args:
        audio_file_path (str): Path to the input audio file.
        chunk_duration (int): Duration of each chunk in seconds (default: 300).
        output_dir (str): Directory to save the output chunks.
        overlap (int): Overlap between chunks in seconds.

    Returns:
        list: List of file paths for the generated chunks.
    """
    if not os.path.exists(audio_file_path):
        logging.error(f"File does not exist: {audio_file_path}")
        raise FileNotFoundError(f"File not found: {audio_file_path}")
    
    audio = AudioSegment.from_file(audio_file_path)

    # Create output directory if not exists
    os.makedirs(output_dir, exist_ok=True)

    chunk_duration_ms = chunk_duration * 1000
    overlap_ms = overlap * 1000
    chunks = []
    start_time = 0

    while start_time < len(audio):
        end_time = min(start_time + chunk_duration_ms, len(audio))
        chunk = audio[start_time:end_time]
        chunk_filename = os.path.join(output_dir, f"chunk_{len(chunks) + 1}.wav")
        chunk.export(chunk_filename, format="wav")
        chunks.append(chunk_filename)
        start_time += chunk_duration_ms - overlap_ms

    logging.info(f"Audio split into {len(chunks)} chunks.")
    return chunks
