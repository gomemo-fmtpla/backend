from app.commons.environment_manager import load_env
from openai import OpenAI
import os
import json

load_env()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_quizzes(transcript: str, languange: str = "") -> dict:
    """Generate a set of quizzes with multiple-choice questions and answer indices from the provided transcript using OpenAI."""
    try:
        quizzes_text = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    Please generate a set of quiz questions based on the following content using the languange of {languange}.

                    if the languange is empty or not provided, then autodetect the languange.

                    {transcript}

                    The output should be in JSON format and should include an array of quizzes, where each quiz has:
                    - A "question"
                    - Four "choices" as a list (e.g., ["Choice 1", "Choice 2", "Choice 3", "Choice 4"])
                    - The correct "answer" as an index (an integer between 0 and 3) that corresponds to one of the choices

                    The structure should be as follows:

                    [
                        {{
                            "question": "Question 1",
                            "choices": ["Choice 1", "Choice 2", "Choice 3", "Choice 4"],
                            "answer": 0
                        }},
                        {{
                            "question": "Question 2",
                            "choices": ["Choice 1", "Choice 2", "Choice 3", "Choice 4"],
                            "answer": 1
                        }},
                        ...
                    ]

                    For the answer, DO NOT! include any additional text, explanations, or tags. 
                    Provide only the JSON array! 
                    """,
                }
            ],
            model="gpt-4o-mini",
        )
      
        # Extract the 'content' field
        quizzes_json_str = quizzes_text.choices[0].message.content
        quizzes = json.loads(quizzes_json_str)

        return {
            "success": True,
            "data": {
                "quizzes": quizzes
            },
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": "QuizGenerationError",
                "message": str(e)
            }
        }