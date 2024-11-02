from app.commons.environment_manager import load_env
from openai import OpenAI
from groq import Groq
import os

load_env()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_chat(chat_input: str="", summary: str="", language: str="") -> dict:
    try:
        response_text = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": f"Please generate a chat response of the following content based on {summary} using the language of {language}. If the language is empty or not provided, then autodetect the language."
                },
                {
                    "role": "user",
                    "content": chat_input
                }
            ],
        )
        # Extract the 'content' field
        chat_completion = response_text.choices[0].message.content.strip()

        # Parse the JSON response
        import json
        try:
            return {
                "success": True,
                "data": {
                    "answer": chat_completion
                },
                "error": None
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": {
                    "type": "JSONDecodeError",
                    "message": f"Failed to decode JSON: {str(e)}"
                }
            }

    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": "ChatGenerationError",
                "message": str(e)
            }
        }