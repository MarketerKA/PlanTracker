from fastapi import FastAPI, Depends, HTTPException, status, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import os
from . import models, schemas, auth, config
from .database import engine, get_db
import re
from email_validator import validate_email, EmailNotValidError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="PlanTracker API")

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

# Form-based token endpoint for OAuth2 compatibility
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    logger.info(f"Token request for username: {form_data.username}")
    
    # Verify user exists and password is correct
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Authentication failed for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Token generated for user: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

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
    db_activity = models.Activity(**activity.dict(), user_id=current_user.id)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    logger.info(f"Activity created by user: {current_user.email}, activity ID: {db_activity.id}")
    return db_activity

@app.get("/activities/", response_model=List[schemas.Activity])
def read_activities(
    skip: int = 0,
    limit: int = 15,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    activities = db.query(models.Activity).filter(
        models.Activity.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    logger.info(f"Activities retrieved for user: {current_user.email}, count: {len(activities)}")
    return activities

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
    
    for key, value in activity.dict(exclude_unset=True).items():
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