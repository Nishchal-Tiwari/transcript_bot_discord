import json

def combine_and_sort_transcriptions(data):
    # Extract all transcriptions into a single list with username included
    transcriptions = []
    for username, speaker_data in data['data'].items():
        for transcription in speaker_data['transcription']:
            # Add the username to the transcription object
            transcription_with_user = transcription.copy()
            transcription_with_user['username'] = username
            transcriptions.append(transcription_with_user)
    
    # Sort transcriptions first by startTime, then by endTime
    sorted_transcriptions = sorted(transcriptions, key=lambda x: (x['startTime'], x['endTime']))
    
    return sorted_transcriptions

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
    return '\n'.join(formatted_transcriptions)
    
        
        
    
    return a

# Example usage
data = {
    "data": {
        "DeltaXPR": {
            "transcription": [
                {
                    "endTime": 1,
                    "startTime": 1.23,
                    "text": "Hello Pavan"
                }
            ]
        },
        "SmìLe": {
            "transcription": [
                {
                    "endTime": 1.23,
                    "startTime": 1.23,
                    "text": "hello hello test one two three"
                }
            ]
        }
    }
}

sorted_transcriptions = combine_and_sort_transcriptions(data)
print(format_transcriptions(sorted_transcriptions))