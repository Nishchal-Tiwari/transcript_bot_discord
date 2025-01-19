import json

def format_chat_transcript(data):
    formatted_transcript = """Chat Transcript\n\n"""
    
    for idx, messages in enumerate(data.get("data", []), start=1):
        for message in messages:
            user_id = message.get("user_id", "Unknown")
            start_time = message.get("start", 0.0)
            end_time = message.get("end", 0.0)
            text = message.get("text", "[No Message]")
            
            # Format each message
            formatted_transcript += (
                f"{idx}. {user_id}(" \
                f"{format_time(start_time)} - {format_time(end_time)}):  \n"
                f"\"{text}\"\n\n"
            )

    return formatted_transcript

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"