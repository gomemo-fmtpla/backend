# generate the summary in md format
from app.commons.environment_manager import load_env
from openai import OpenAI
import os

load_env()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_summary(transcript: str) -> dict:
    """Generate a summary from the provided transcript using OpenAI."""
    try:
        summary_text = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""
                Please generate a detailed markdown summary of the following content:

                {transcript}

                The summary should include:
                - A title (using `#` for the main title)
                - Subheadings (using `##` for subtitles)
                - Bullet points for key points
                - Code blocks or other markdown features if applicable
                - A conclusion section

                Additionally, provide:
                - A single phrase to categorize the content (e.g., 'Tutorial', 'Guide', 'Report', 'General')
                - An emoji that represents the content category

                The output must be in the following JSON format:

                {{
                    "content_category": "Category Phrase",
                    "emoji_representation": "Emoji",
                    "markdown": "Markdown content here"
                }}
                """,
                }
            ],
            model="gpt-4o-mini",
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
                    "content_category": parsed_content.get("content_category", ""),
                    "emoji_representation": parsed_content.get("emoji_representation", ""),
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