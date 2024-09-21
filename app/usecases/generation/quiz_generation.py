from app.commons.environment_manager import load_env
from openai import OpenAI
import os
import json

load_env()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

import json

def generate_quizzes(transcript: str, language: str = "") -> dict:
    """Generate a set of quizzes with multiple-choice questions and answer indices from the provided transcript using OpenAI."""
    try:
        quizzes_text = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"Please generate a set of quiz questions based on the following content using the language of {language}. If the language is empty or not provided, then autodetect the language."
                },
                {
                    "role": "user",
                    "content": transcript
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "quiz_generation",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "quizzes": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "question": {"type": "string"},
                                        "choices": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "answer": {"type": "integer"}
                                    },
                                    "required": ["question", "choices", "answer"],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["quizzes"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        )
      
        # Extract the 'content' field
        quizzes_json_str = quizzes_text.choices[0].message.content
        quizzes = json.loads(quizzes_json_str)

        return {
            "success": True,
            "data": {
                "quizzes": quizzes["quizzes"]
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
