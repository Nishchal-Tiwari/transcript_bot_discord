import json
import os
import time 
from transcribe_library.whisper_online import transcribe_audio
def read_json_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No such file: '{file_path}'")
    
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    return data
def get_transcription_results(file_path):
    data = read_json_file(file_path)
    transcription_arrays = []
    for user in data["users"]:
        t_data = transcribe_audio(user["file_path"], user["user_name"])
        transcription_arrays.append(t_data)
        print(json.dumps(t_data, indent=4))
    output_path = 'transcription/' + data["channel_name"] + '_' + str(int(time.time())) + '.json'
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_path, "w", encoding="utf-8") as info_file:
        json.dump({"data": transcription_arrays}, info_file, indent=4)
    return transcription_arrays


def sort_transcription_results(transcription_results):
    return sorted(transcription_results, key=lambda x: (x["start"], x["end"]))

# file_path = '/Users/nishchaltiwari/dev/pvt/zerve/recordings/general_20250118_195138/info.json'
# get_transcription_results(file_path)