from app.commons.environment_manager import load_env
from openai import OpenAI
import os

load_env()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def translate_summary(summary: str, lang: str) -> dict:
    """Translate a summary from the provided summary using OpenAI."""
    try:
        # Prepare the prompt for translation
        prompt = f"""
        Translate the following summary into {lang}:

        {summary}
        """
        
        # Make a request to the OpenAI API for translation
        translation_response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="gpt-4",  # Use the appropriate GPT-4 model
        )
        
        # Extract the 'content' field from the response
        content = translation_response.choices[0].message['content']
        
        return {
            "success": True,
            "data": {
                "translated_summary": content
            },
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": "TranslationError",
                "message": str(e)
            }
        }
