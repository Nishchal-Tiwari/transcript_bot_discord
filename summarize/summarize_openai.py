from openai import OpenAI
import json
import os
api_key = os.getenv("OPENAPI_KEY")

client = OpenAI(
    api_key=api_key
)


def extract_text(data):
    text = " ".join([entry['text'] for entry in data[0]])
    return text

def summarize_text(text):
    response = client.chat.completions.create(
        model="gpt-4o",
        # prompt=f"Summarize the following meeting transcript in a point-wise format:\n{text}",
         messages=[
        {
            "role": "user",
          "content": f"Analyze the following meeting transcript and create a detailed summary. Include the following sections in the output: 1. **Meeting Title**: A concise and relevant title summarizing the meeting's purpose or main topic. 2. **Key Topics Discussed**: A bullet-point list of the main discussion points or agenda items covered during the meeting. 3. **Decisions Made**: Highlight the key decisions made during the meeting. 4. **Action Items**: Provide a list of actionable tasks assigned to specific participants, including deadlines where mentioned. 5. **Insights and Outcomes**: Summarize the key insights, agreements, or conclusions drawn from the meeting. 6. **Challenges and Concerns**: Mention any issues or challenges raised during the discussion. 7. **Propaganda (Meeting Objectives)**: Write a paragraph summarizing the meeting's overarching objectives or goals. 8. **Summary of Meeting**: Provide a concise and readable summary of the meeting, capturing the flow of discussion, key arguments, and relevant details. Transcript: {text}"
        }
    ],
        # temperature=0.7,
        # max_tokens=300
    )
    # print(response)
    summary = response.choices[0].message.content
    return summary

input_data = {
    "data": [
        [
            {
                "user_id": "DeltaXPR",
                "start": 0.0,
                "end": 7.0,
                "text": "I joined Accenture as an ASE role and all the things were very nice when I was"
            },
            {
                "user_id": "DeltaXPR",
                "start": 7.0,
                "end": 13.119999885559082,
                "text": "joined it on 18th of September 2024 and as a fresher I think Accenture is a good"
            },
            {
                "user_id": "DeltaXPR",
                "start": 13.119999885559082,
                "end": 22.559999465942383,
                "text": "company if you are comparing with others but if I compare the work-life"
            },
            {
                "user_id": "DeltaXPR",
                "start": 22.559999465942383,
                "end": 28.239999771118164,
                "text": "balance and other things like how the Accenture provide the skills to their"
            },
            {
                "user_id": "DeltaXPR",
                "start": 28.239999771118164,
                "end": 35.84000015258789,
                "text": "trainees and the other things like every Friday they conduct a meeting for their"
            },
            {
                "user_id": "DeltaXPR",
                "start": 35.84000015258789,
                "end": 41.91999816894531,
                "text": "employees like fun Friday like things and the main thing which I experienced"
            },
            {
                "user_id": "DeltaXPR",
                "start": 41.91999816894531,
                "end": 46.84000015258789,
                "text": "in Accenture as a fresher is you don't have any kind of workload in it if you"
            },
            {
                "user_id": "DeltaXPR",
                "start": 46.84000015258789,
                "end": 58.880001068115234,
                "text": "have a mood to go to every day hello my name is Alok Kumar Singh"
            }
        ]
    ]
}

# meeting_text = extract_text(input_data['data'])
# summary = summarize_text(input_data['data'])
# print("Meeting Summary:")
# print(summary)
