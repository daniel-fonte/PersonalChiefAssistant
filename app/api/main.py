from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from app.api.lifespan import lifespan
from app.api.routes.chat import router as chat_router

app = FastAPI(title="Personal Chief API", version="1.0.0", lifespan=lifespan)
app.include_router(chat_router)
