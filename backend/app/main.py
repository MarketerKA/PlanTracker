from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers.activity_router import activity_router
from .routers.tag_router import tag_router
from .routers.user_router import user_router


# Create database tables
models.Base.metadata.create_all(bind=engine)


# Initialize FastAPI app
app = FastAPI(title="PlanTracker API")

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
