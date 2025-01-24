import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
import json
import asyncio
# Configure the API key for Gemini
genai.configure(api_key="AIzaSyANdph5Yv3x8Pan-TDw8cmq1FBIOYMQeAo")


def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file


# Define the generation configuration with schema
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 20000,
    "response_schema": content.Schema(
        type=content.Type.OBJECT,
        required=["transcription"],
        properties={
            "transcription": content.Schema(
                type=content.Type.ARRAY,
                items=content.Schema(
                    type=content.Type.OBJECT,
                    properties={
                        "startTime": content.Schema(type=content.Type.NUMBER),
                        "endTime": content.Schema(type=content.Type.NUMBER),
                        "text": content.Schema(type=content.Type.STRING),
                    },
                    required=["startTime", "endTime", "text"],
                ),
                description="Detailed transcription in the specified format.startTime is starting of that text and endTime is ending of a complete sentence keep in mind complete sentence .",
            ),
        },
    ),
    "response_mime_type": "application/json",
}

# Create the generative model instance
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)


async def getTranscription(file_path):
    """Process the audio file and generate a summary."""
    # Upload the audio file
    audio_file = upload_to_gemini(file_path, mime_type="audio/wav")

    # Start a chat session with the uploaded audio
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [audio_file],
            },
        ]
    )
    # Send the message to transcribe and summarize
    response = chat_session.send_message(
        "Please transcribe this audio ")
    # print(response)
    return json.loads(response.candidates[0].content.parts[0].text)


# Process the audio file and generate a summary


# async def doTask():
#     ans = await process_audio_file(
#         "/Users/nishchaltiwari/dev/pvt/zerve/recordings/general_20250123_001645/recording_DeltaXPR_20250123_001645.wav")
#     print(json.dumps(ans, indent=2))

# # Run the async function
# if __name__ == "__main__":
#     asyncio.run(doTask())
