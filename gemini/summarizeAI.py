import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
import json
import asyncio
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_KEY")
# Configure the API key for Gemini
genai.configure(api_key=api_key)

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
        required=["summary", "tasks", "important_points"],
        properties={
            "summary": content.Schema(
                type=content.Type.STRING,
                description="A concise summary of the conversation."
            ),
            "tasks": content.Schema(
                type=content.Type.ARRAY,
                items=content.Schema(
                    type=content.Type.OBJECT,
                    properties={
                        "task": content.Schema(type=content.Type.STRING),
                        "priority": content.Schema(type=content.Type.STRING, enum=["High", "Medium", "Low"]),
                    },
                ),
                description="Tasks discussed in the audio with priorities."
            ),
            "important_points": content.Schema(
                type=content.Type.ARRAY,
                items=content.Schema(type=content.Type.STRING),
                description="Key discussion points or critical information."
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


async def get_summary(transcription):
    """Process the audio file and generate a summary."""
    # Upload the audio file
    # audio_file = upload_to_gemini(file_path, mime_type="audio/wav")

    # Start a chat session with the uploaded audio
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": transcription,
            },
        ]
    )
    # Send the message to transcribe and summarize
    response = chat_session.send_message(
        "Using the text  and provide a summary of the text,provide the tasks discussed in the text only add if explictly defined as task or todo, and key discussion points also .")
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
