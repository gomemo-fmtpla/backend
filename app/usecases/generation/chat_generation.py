from app.commons.environment_manager import load_env
# from openai import OpenAI
# from groq import Groq
import replicate
import os

load_env()

client = replicate.Client(
    api_token=os.getenv("REPLICATE_API_TOKEN")
)

def generate_chat(chat_input: str="", summary: str="", language: str="") -> dict:
    try:
        input_data = {
            "system_prompt": f"""
                You are an assistant that answers questions solely based on the following context:
                
                {summary}
                
                If the user's question is not relevant to this context, respond with 'This question doesn't seem related to the note. Do you have another question?'. 
                Answer in the specified language {language}. If {language} is empty or not provided, automatically detect the language of the context and respond in that language.
            """,
            "prompt": chat_input,
        }

        output = client.stream(
            "meta/meta-llama-3-8b-instruct",
            input=input_data                  
        )
        
        formatted_output = ''.join(output).replace("\n", "")

        # Parse the JSON response
        import json
        try:
            return {
                "success": True,
                "data": {
                    "answer": formatted_output
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