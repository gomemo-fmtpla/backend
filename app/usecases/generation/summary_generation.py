# generate the summary in md format
from app.commons.environment_manager import load_env
from openai import OpenAI
import os

load_env()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_summary(transcript: str, language: str="", context: str = "") -> dict:
    """Generate a summary from the provided transcript using OpenAI."""
    try:
        summary_text = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"Please generate a detailed markdown summary of the following content using the language of {language}. If the language is empty or not provided, then autodetect the language."
                },
                {
                    "role": "user",
                    "content": f"""
                        {transcript}

                        The context of the transcript is context = {context}. If the context is not provided, then interpret it from the transcript.

                        Please generate a detailed markdown summary that includes:
                        - A title (using `#` for the main title)
                        - Subheadings (using `##` for subtitles)
                        - Bullet points for key points
                        - Code blocks or other markdown features if applicable
                        - A conclusion section

                        Additionally, provide:
                        - A single phrase to categorize the content, e.g., technology, physics, food, animal
                        - An emoji that represents the content category
                        - Provide the language code of the content using ISO 639 language codes, e.g., eng, fra.

                        The output must be in the following JSON format:

                        {{
                            "title" : "A concise title separate from the markdown title",
                            "content_category": "Category Phrase (capitalize the first letter)",
                            "emoji_representation": "Emoji",
                            "lang": "language code here",
                            "markdown": "Markdown content with properly escaped characters"
                        }}

                        The output must be well-structured, JSON formatted, and handle escape characters. Only return the JSON object, no additional tags or prefixes.
                    """
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "summary_generation",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "content_category": {"type": "string"},
                            "emoji_representation": {"type": "string"},
                            "lang": {"type": "string"},
                            "markdown": {"type": "string"}
                        },
                        "required": ["title", "content_category", "emoji_representation", "lang", "markdown"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        )
        # Extract the 'content' field
        content = summary_text.choices[0].message.content.strip()

        # Parse the JSON response
        import json
        try:
            parsed_content = json.loads(content)
            return {
                "success": True,
                "data": {
                    "title": parsed_content.get("title"),
                    "content_category": parsed_content.get("content_category", ""),
                    "emoji_representation": parsed_content.get("emoji_representation", ""),
                    "lang": parsed_content.get("lang", "eng"),
                    "markdown": parsed_content.get("markdown", "")
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
                "type": "SummaryGenerationError",
                "message": str(e)
            }
        }