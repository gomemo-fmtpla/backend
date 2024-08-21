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
                Please provide a detailed markdown summary of the following content:

                {transcript}

                The summary should include:
                - A title (using `#` for the main title)
                - Subheadings (using `##` for subtitles)
                - Bullet points for key points
                - Code blocks or other markdown features if applicable
                - A conclusion section

                The output must be well-structured and in markdown format.
                """,
                }
            ],
            model="gpt-4o-mini",
        )
      
        # Extract the 'content' field
        content = summary_text.choices[0].message.content
        print(content)

        return {
            "success": True,
            "data": {
                "summary": content
            },
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "type": "SummaryGenerationError",
                "message": str(e)
            }
        }
