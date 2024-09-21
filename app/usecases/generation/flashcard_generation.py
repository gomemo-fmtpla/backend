from app.commons.environment_manager import load_env
from openai import OpenAI
import os
import json

load_env()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_flashcards(transcript: str, language: str = "") -> dict:
    """Generate a set of flashcards from the provided transcript using OpenAI."""
    try:
        flashcards_text = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"Please generate a set of flashcards based on the following content using the language of {language}. If the language is empty or not provided, then autodetect the language."
                },
                {
                    "role": "user",
                    "content": transcript
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "flashcard_generation",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "flashcards": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "question": {"type": "string"},
                                        "answer": {"type": "string"}
                                    },
                                    "required": ["question", "answer"],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["flashcards"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        )
        # Extract the 'content' field
        flashcards_json_str = flashcards_text.choices[0].message.content
        flashcards = json.loads(flashcards_json_str)

        return {
            "success": True,
            "data": {
                "flashcards": flashcards["flashcards"]
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
