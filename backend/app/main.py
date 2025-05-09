from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models, telegram_bot
from .database import engine
from contextlib import asynccontextmanager
from .routers.activity_router import activity_router
from .routers.tag_router import tag_router
from .routers.user_router import user_router


# Create database tables
models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    try:
        # Start the telegram bot
        await telegram_bot.start_bot()
        yield
    finally:
        # Stop the telegram bot
        await telegram_bot.stop_bot()


# Initialize FastAPI app
app = FastAPI(title="PlanTracker API", lifespan=lifespan)


# Add health check endpoint


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(user_router)
app.include_router(activity_router)
app.include_router(tag_router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
