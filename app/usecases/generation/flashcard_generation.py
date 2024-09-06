from app.commons.environment_manager import load_env
from openai import OpenAI
import os
import json

load_env()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_flashcards(transcript: str, languange: str = "") -> dict:
    """Generate a set of flashcards from the provided transcript using OpenAI."""
    try:
        flashcards_text = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    Please generate a set of flashcards based on the following content using the languange of {languange}.

                    if the languange is empty or not provided, then autodetect the languange.

                    {transcript}

                    The output should be in JSON format and should include an array of flashcards, where each flashcard has a "question" and an "answer". The structure should be as follows:

                    [
                        {{"question": "Question 1", "answer": "Answer 1"}},
                        {{"question": "Question 2", "answer": "Answer 2"}},
                        ...
                    ]

                    Provide only the JSON array. DO NOT include any additional text, explanations, or tags, event markdown TAG. 
                    Also handle the excape character. 
                    """,
                }
            ],
            model="gpt-4o-mini",
        )

        # Extract the 'content' field
        flashcards_json_str = flashcards_text.choices[0].message.content
        flashcards = json.loads(flashcards_json_str)

        return {
            "success": True,
            "data": {
                "flashcards": flashcards
            },
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": "FlashcardGenerationError",
                "message": str(e)
            }
        }
