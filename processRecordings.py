import os
from gemini.transcriptionAi import getTranscription
from gemini.summarizeAI import get_summary
from toolbox.audio import reencode_audio
import json
import asyncio
import time
def read_json_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No such file: '{file_path}'")
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data
    
async def get_transcription_results(file_path):
    data = read_json_file(file_path)
    transcriptions = {}
    for user in data["users"]:
        audio_file_path = user["file_path"]
        reencoded_path = f"{os.path.splitext(audio_file_path)[0]}_reencoded.wav"
        reencode_audio(audio_file_path, reencoded_path)
        transcription = await getTranscription(reencoded_path)
        if os.path.exists(reencoded_path):
            os.remove(reencoded_path)
            print(f"Deleted re-encoded file : {reencoded_path}")
        transcriptions[user["user_name"]] = transcription
    transcription_file_path = 'transcription/' + data["channel_name"] + '_' + str(int(time.time())) + '.json'
    transcription_dir = os.path.dirname(transcription_file_path)
    if not os.path.exists(transcription_dir):
        os.makedirs(transcription_dir)
    with open(transcription_file_path, "w", encoding="utf-8") as info_file:
        json.dump({"data": transcriptions}, info_file, indent=4)
    return transcriptions

def combine_and_sort_transcriptions(data):
    # Extract all transcriptions into a single list with username included
    transcriptions = []
    for username, speaker_data in data.items():
        for transcription in speaker_data['transcription']:
            # Add the username to the transcription object
            transcription_with_user = transcription.copy()
            transcription_with_user['username'] = username
            transcriptions.append(transcription_with_user)
    
    # Sort transcriptions first by startTime, then by endTime
    sorted_transcriptions = sorted(transcriptions, key=lambda x: (x['startTime'], x['endTime']))
    
    return sorted_transcriptions
def get_txt(sorted_transcriptions):
    formatted_transcriptions = ""
    
    for transcription in sorted_transcriptions:
        text = transcription['text']
        formatted_transcriptions= formatted_transcriptions + text + " "
    return formatted_transcriptions
def format_transcriptions(sorted_transcriptions):
    formatted_transcriptions = []
    
    for transcription in sorted_transcriptions:
        # Extract the username, start time, end time, and text
        username = transcription['username']
        start_time = transcription['startTime']
        end_time = transcription['endTime']
        text = transcription['text']
        
        # Format the time into MM:SS format
        def format_time(seconds):
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes:02d}:{seconds:02d}"
        
        start_time_formatted = format_time(start_time)
        end_time_formatted = format_time(end_time)
        
        # Create the formatted string
        formatted_string = f"{username} ({start_time_formatted} - {end_time_formatted}): {text}"
        formatted_transcriptions.append(formatted_string)
    return formatted_transcriptions
async def processRecording(file_path):
    ans = await get_transcription_results(file_path)
    ans1 = await get_summary(get_txt(combine_and_sort_transcriptions(ans)))
    ans3 = combine_and_sort_transcriptions(ans)
    ans4 = format_transcriptions(ans3)
    formatted_transcriptions = '\n'.join(ans4)
    ans1["transcription"] = formatted_transcriptions
    
    print(json.dumps(ans1, indent=4))
    return ans1

# if __name__ == "__main__":
#     file_path = '/Users/nishchaltiwari/dev/pvt/zerve/recordings/general_20250125_005239/info.json'
#     asyncio.run(processRecording(file_path))