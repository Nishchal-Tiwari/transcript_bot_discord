import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
import json
import asyncio
import logging
from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()

class GeminiSummarizer:
    def __init__(self, api_key=os.getenv('GEMINI_KEY')):
        """
        Initializes the GeminiSummarizer class with the required configurations.

        Args:
            api_key (str): API key for the Gemini service.
        """
        if not api_key:
            raise ValueError("API key for Gemini must be provided.")

        self.api_key = api_key
        genai.configure(api_key=self.api_key)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s]: %(message)s",
        )

        # Define the generation configuration
        self.generation_config = {
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
                                "priority": content.Schema(
                                    type=content.Type.STRING,
                                    enum=["High", "Medium", "Low"]
                                ),
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

        # Initialize the generative model
        try:
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=self.generation_config,
            )
            logging.info("Generative model initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize generative model: {e}")
            raise

    def get_summary(self, transcription):
        """
        Process the transcription and generate a structured summary using the Gemini API.

        Args:
            transcription (str): The transcription text to be summarized.

        Returns:
            dict: A structured summary containing 'summary', 'tasks', and 'important_points'.
        """
        if not transcription :
            logging.error("Invalid transcription provided. It must be a non-empty string.")
            raise ValueError("Transcription must be a valid non-empty string.")

        try:
            # Start a chat session with the transcription
            logging.info("Starting chat session with Gemini API for transcription summarization.")
            chat_session = self.model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": transcription,
                    },
                ]
            )

            # Send a message to summarize the transcription
            response = chat_session.send_message(
                "Using the provided text, generate a summary of the text. "
                "Provide the tasks discussed in the text (only if explicitly defined as tasks or to-dos), "
                "and key discussion points as well."
            )

            # Validate response
            if not response or not response.candidates:
                logging.error("Empty or invalid response received from Gemini API.")
                raise ValueError("No valid response from Gemini API.")

            # Parse response content
            structured_summary = json.loads(response.candidates[0].content.parts[0].text)
            logging.info("Successfully generated structured summary.")
            return structured_summary

        except Exception as e:
            logging.error(f"Error during transcription summarization: {e}")
            raise

    @staticmethod
    def load_data(file_path):
        """
        Load transcription data from a JSON file.

        Args:
            file_path (str): Path to the JSON file containing transcription data.

        Returns:
            dict: The transcription data loaded from the file.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            logging.error(f"Error loading data from file: {e}")
            raise

# # Example usage
# if __name__ == "__main__":
#     # Example transcription file
#     file_path = "/Users/nishchaltiwari/dev/pvt/zerve2/transcription_results.json"

#     # Instantiate the summarizer class
#     api_key = "AIzaSyANdph5Yv3x8Pan-TDw8cmq1FBIOYMQeAo"
#     summarizer = GeminiSummarizer(api_key=api_key)

#     try:
#         # Load transcription data
#         transcription_data = summarizer.load_data(file_path)

#         # Run the summary generation
#         summary = asyncio.run(summarizer.get_summary(json.dumps(transcription_data)))
#         print(json.dumps(summary, indent=4))

#         # Save summary to a file
#         output_file = "summary_output.json"
#         with open(output_file, "w", encoding="utf-8") as f:
#             json.dump(summary, f, indent=4)
#         logging.info(f"Summary saved to {output_file}")

#     except Exception as e:
#         logging.error(f"Failed to process transcription: {e}")
