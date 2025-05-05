from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models, telegram_bot
from .database import engine
from contextlib import asynccontextmanager
import asyncio
from .routers.activity_router import activity_router
from .routers.tag_router import tag_router
from .routers.user_router import user_router


# Create database tables
models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    bot_task = asyncio.create_task(telegram_bot.start_bot())
    try:
        yield
    finally:
        await telegram_bot.stop_bot()
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass


# Initialize FastAPI app
app = FastAPI(title="PlanTracker API", lifespan=lifespan)

app.include_router(user_router)
app.include_router(activity_router)
app.include_router(tag_router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
