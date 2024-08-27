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
        translation_response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""
                        Translate the following transcript into the language of {lang}:

                        {summary}                
                    """,
                }
            ],
            model="gpt-4o-mini",
        )
        
        # Access the 'content' field correctly
        content = translation_response.choices[0].message.content.strip()
    
        return {
            "success": True,
            "data": {
                "translated_text": content
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
