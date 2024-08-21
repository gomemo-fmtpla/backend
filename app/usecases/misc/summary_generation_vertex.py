from langchain_google_vertexai import ChatVertexAI

def generate_summary_vertex(transcript: str) -> dict:
    model = ChatVertexAI(model="gemini-1.5-pro")

    try:
        prompt = f"Summarize the following transcript in Markdown format:\n\n{transcript}\n\nSummary:"
        generation = model.invoke(prompt)
        print(generation)
        return {
            "success": True,
            "data": {
                "summary": generation
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
