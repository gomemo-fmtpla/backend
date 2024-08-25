from fastapi import FastAPI
from app.commons.environment_manager import load_env
import os

from app.route.user import router as user_router
from app.route.note import router as note_router
from app.route.summary import router as summary_router
from app.route.flashcard import router as flashcard_router
from app.route.quiz import router as quiz_router
# from app.route.text_route import text_router

load_env()
app = FastAPI(title=os.getenv("APP_NAME"))

app.include_router(user_router)
app.include_router(note_router)
app.include_router(summary_router)
app.include_router(flashcard_router)
app.include_router(quiz_router)
# app.include_router(text_router, prefix="/v1/text", tags=["text"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


