from fastapi import FastAPI, Depends, HTTPException, status, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import os
from . import models, schemas, auth, config, telegram_bot
from .database import engine, get_db
import re
from contextlib import asynccontextmanager
import asyncio
from email_validator import validate_email, EmailNotValidError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Validate email with email-validator library
def validate_email_address(email: str) -> bool:
    try:
        # Validate and get normalized result
        valid = validate_email(email, check_deliverability=True)
        
        # Check for common test domains
        domain = email.split('@')[1].lower()
        if domain in ['example.com', 'test.com', 'example.org']:
            logger.warning(f"Rejected test domain: {domain}")
            return False
            
        # Email is valid and the domain has SMTP Server
        logger.info(f"Email validated successfully: {valid.normalized}")
        return True
    except EmailNotValidError as e:
        logger.warning(f"Email validation failed: {str(e)}")
        return False

# Calculate elapsed time between timer start and now
def calculate_elapsed_time(activity):
    if activity.timer_status == "running" and activity.last_timer_start:
        # Calculate time since timer was started
        elapsed = datetime.now() - activity.last_timer_start
        # Convert to seconds
        return int(elapsed.total_seconds())
    return 0

# User registration and authentication endpoints
@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Log the request
    logger.info(f"User registration attempt: {user.email}")
    
    # Check if user with this email already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        logger.warning(f"Registration failed: Email already registered: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate email with email-validator library
    if not validate_email_address(user.email):
        logger.warning(f"Registration failed: Invalid email address: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address. Please provide a valid email."
        )
    
    # Hash the password
    hashed_password = auth.get_password_hash(user.password)
    
    # Create new user
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password
    )
    
    # Save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"User registered successfully: {user.email}")
    return db_user


# JSON-based login endpoint for frontend applications
@app.post("/login", response_model=schemas.Token)
async def login_json(
    login_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"Login attempt for email: {login_data.email}")
    
    # Verify user exists and password is correct
    user = auth.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        logger.warning(f"Authentication failed for email: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Login successful for user: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

# Get current user profile
@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    logger.info(f"Profile accessed by user: {current_user.email}")
    return current_user

# Activity endpoints
@app.post("/activities/", response_model=schemas.Activity)
def create_activity(
    activity: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Get tags from activity data
    tag_names = activity.tags
    tags = []
    
    # Create activity dictionary without tags
    activity_data = activity.dict(exclude={"tags"})
    activity_data["user_id"] = current_user.id
    
    # Create new activity
    db_activity = models.Activity(**activity_data)
    
    # Associate tags with the activity
    for tag_name in tag_names:
        # Check if tag exists
        tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
        if not tag:
            # Create new tag if it doesn't exist
            tag = models.Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        db_activity.tags.append(tag)
    
    # Save activity to database
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    
    logger.info(f"Activity created by user: {current_user.email}, activity ID: {db_activity.id}")
    return db_activity

@app.get("/activities/", response_model=List[schemas.Activity])
def read_activities(
    skip: int = 0,
    limit: int = 15,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Base query for user's activities
    query = db.query(models.Activity).filter(
        models.Activity.user_id == current_user.id
    )
    
    # Filter by tag if provided
    if tag:
        query = query.join(models.Activity.tags).filter(models.Tag.name == tag)
    
    # Get activities with pagination
    activities = query.order_by(models.Activity.start_time.desc()).offset(skip).limit(limit).all()
    
    # Update timer status for running timers
    for activity in activities:
        if activity.timer_status == "running":
            elapsed = calculate_elapsed_time(activity)
            activity.recorded_time += elapsed
            
    logger.info(f"Activities retrieved for user: {current_user.email}, count: {len(activities)}")
    return activities

@app.get("/activities/{activity_id}", response_model=schemas.Activity)
def read_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Get activity
    db_activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.user_id == current_user.id
    ).first()
    
    if not db_activity:
        logger.warning(f"Activity {activity_id} not found for user {current_user.email}")
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Update recorded time if timer is running
    if db_activity.timer_status == "running" and db_activity.last_timer_start:
        elapsed = calculate_elapsed_time(db_activity)
        db_activity.recorded_time += elapsed
        db_activity.last_timer_start = datetime.now()
        db.commit()
    
    logger.info(f"Activity {activity_id} retrieved by user: {current_user.email}")
    return db_activity

@app.put("/activities/{activity_id}", response_model=schemas.Activity)
def update_activity(
    activity_id: int,
    activity: schemas.ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.user_id == current_user.id
    ).first()
    if not db_activity:
        logger.warning(f"Activity update failed: Activity {activity_id} not found for user {current_user.email}")
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Update activity with provided data
    update_data = activity.dict(exclude_unset=True)
    
    # Handle tags separately if provided
    if "tags" in update_data:
        tag_names = update_data.pop("tags")
        # Clear existing tags
        db_activity.tags = []
        # Add new tags
        for tag_name in tag_names:
            # Check if tag exists
            tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
            if not tag:
                # Create new tag if it doesn't exist
                tag = models.Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            db_activity.tags.append(tag)
    
    # Update other fields
    for key, value in update_data.items():
        setattr(db_activity, key, value)
    
    db.commit()
    db.refresh(db_activity)
    logger.info(f"Activity {activity_id} updated by user: {current_user.email}")
    return db_activity

@app.delete("/activities/{activity_id}")
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.user_id == current_user.id
    ).first()
    if not db_activity:
        logger.warning(f"Activity deletion failed: Activity {activity_id} not found for user {current_user.email}")
        raise HTTPException(status_code=404, detail="Activity not found")
    
    db.delete(db_activity)
    db.commit()
    logger.info(f"Activity {activity_id} deleted by user: {current_user.email}")
    return {"message": "Activity deleted successfully"}

# Timer functionality endpoints
@app.post("/activities/{activity_id}/timer", response_model=schemas.Activity)
async def activity_timer(
    activity_id: int,
    timer_action: schemas.TimerAction,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Get activity
    db_activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id,
        models.Activity.user_id == current_user.id
    ).first()
    
    if not db_activity:
        logger.warning(f"Timer action failed: Activity {activity_id} not found for user {current_user.email}")
        raise HTTPException(status_code=404, detail="Activity not found")
    
    action = timer_action.action.lower()
    current_time = datetime.now()
    
    # Handle timer actions
    if action == "start":
        # If timer was already running, do nothing
        if db_activity.timer_status == "running":
            logger.info(f"Timer already running for activity {activity_id}")
            return db_activity
        
        # If timer was paused, just change status and update start time
        if db_activity.timer_status == "paused":
            db_activity.timer_status = "running"
            db_activity.last_timer_start = current_time
        
        # If timer was stopped, reset start time and change status
        if db_activity.timer_status == "stopped":
            db_activity.timer_status = "running"
            db_activity.last_timer_start = current_time
        
        # Sending a notification to Telegram
        if current_user.telegram_chat_id:
            await telegram_bot.send_notification(
                current_user.id,
                f"▶️ Timer started for task: {db_activity.title}"
            )
            
        logger.info(f"Timer started for activity {activity_id} by user {current_user.email}")
        
    elif action == "pause":
        # Can only pause a running timer
        if db_activity.timer_status != "running":
            logger.warning(f"Cannot pause: Timer not running for activity {activity_id}")
            raise HTTPException(status_code=400, detail="Timer not running")
        
        # Calculate elapsed time since last start and add to recorded time
        elapsed = calculate_elapsed_time(db_activity)
        db_activity.recorded_time += elapsed
        db_activity.timer_status = "paused"
        db_activity.last_timer_start = None
        
        # Sending a notification to Telegram
        if current_user.telegram_chat_id:
            await telegram_bot.send_notification(
                current_user.id,
                f"⏸️ Timer paused for task: {db_activity.title}\n"
                f"Saved time: {telegram_bot.format_time(db_activity.recorded_time)}"
            )
        
        logger.info(f"Timer paused for activity {activity_id} by user {current_user.email}")
        
    elif action == "stop":
        # Can only stop a running or paused timer
        if db_activity.timer_status == "stopped":
            logger.warning(f"Timer already stopped for activity {activity_id}")
            return db_activity
        
        # If running, calculate elapsed time and add to recorded time
        if db_activity.timer_status == "running":
            elapsed = calculate_elapsed_time(db_activity)
            db_activity.recorded_time += elapsed
        
        # Reset timer state
        db_activity.timer_status = "stopped"
        db_activity.last_timer_start = None
        
        if current_user.telegram_chat_id:
            await telegram_bot.send_notification(
                current_user.id,
                f"⏹️ Timer stopped for task: {db_activity.title}\n"
                f"Total time: {telegram_bot.format_time(db_activity.recorded_time)}"
            )
        
        logger.info(f"Timer stopped for activity {activity_id} by user {current_user.email}")
    

    elif action == "save":
        # Can save from any state, but only calculate additional time if running
        if db_activity.timer_status == "running":
            elapsed = calculate_elapsed_time(db_activity)
            db_activity.recorded_time += elapsed
            # Reset timer start time to now
            db_activity.last_timer_start = current_time
            
        logger.info(f"Timer saved for activity {activity_id} by user {current_user.email}")
        
    else:
        logger.warning(f"Invalid timer action: {action} for activity {activity_id}")
        raise HTTPException(status_code=400, detail="Invalid timer action")

    # Save changes to database
    db.commit()
    db.refresh(db_activity)
    
    return db_activity

# Tag endpoints
@app.post("/tags/", response_model=schemas.Tag)
def create_tag(
    tag: schemas.TagCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_tag = models.Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    logger.info(f"Tag {db_tag.name} created by user: {current_user.email}")
    return db_tag

@app.get("/tags/", response_model=List[schemas.Tag])
def read_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    tags = db.query(models.Tag).offset(skip).limit(limit).all()
    logger.info(f"Tags retrieved for user: {current_user.email}, count: {len(tags)}")
    return tags 


@app.get("/users/me/telegram-status")
async def get_telegram_status(current_user: models.User = Depends(auth.get_current_active_user)):
    return {
        "is_linked": bool(current_user.telegram_chat_id),
        "telegram_chat_id": current_user.telegram_chat_id
    }


@app.delete("/users/me/telegram")
async def unlink_telegram(current_user: models.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    if not current_user.telegram_chat_id:
        raise HTTPException(status_code=400, detail="Telegram account not linked")
    
    current_user.telegram_chat_id = None
    db.commit()
    
    return {"message": "Telegram account unlinked successfully"}