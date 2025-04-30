from fastapi import FastAPI, Depends, HTTPException, status, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import os
from . import models, schemas, auth
from .database import engine, get_db
from .email_utils import send_verification_email, generate_verification_code

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="PlanTracker API")

# Get frontend URL from environment variable or use default in development
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User registration and authentication endpoints
@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user with this email already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = auth.get_password_hash(user.password)
    
    # Generate verification code
    verification_code = generate_verification_code()
    
    # Create new user
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        is_verified=False,
        verification_code=verification_code
    )
    
    # Save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send verification email
    try:
        await send_verification_email(user.email, verification_code)
    except Exception as e:
        # Log the error, but continue (don't fail registration if email fails)
        print(f"Error sending verification email: {e}")
    
    return db_user

@app.get("/verify-email", response_class=RedirectResponse)
async def verify_email_link(
    code: str = Query(...), 
    email: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint for email verification via link click
    """
    user = db.query(models.User).filter(
        models.User.email == email,
        models.User.verification_code == code
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification link"
        )
    
    # Update user verification status
    user.is_verified = True
    user.verification_code = None  # Clear the code
    db.commit()
    
    # Redirect to frontend with success message
    return RedirectResponse(f"{FRONTEND_URL}/login?verified=true")

@app.post("/verify-email", response_model=schemas.User)
async def verify_email_code(
    verification_data: schemas.VerifyEmail,
    db: Session = Depends(get_db)
):
    """
    Endpoint for email verification via code
    """
    user = db.query(models.User).filter(
        models.User.email == verification_data.email,
        models.User.verification_code == verification_data.verification_code
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code or email"
        )
    
    # Update user verification status
    user.is_verified = True
    user.verification_code = None  # Clear the code
    db.commit()
    db.refresh(user)
    
    return user

# Form-based token endpoint for OAuth2 compatibility
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Verify user exists and password is correct
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email before logging in."
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# JSON-based login endpoint for frontend applications
@app.post("/login", response_model=schemas.Token)
async def login_json(
    login_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    # Verify user exists and password is correct
    user = auth.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Check if email is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email before logging in."
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Resend verification email
@app.post("/resend-verification")
async def resend_verification(
    email: schemas.UserBase,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email.email).first()
    
    if not user:
        # Don't reveal that the user doesn't exist
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "If your email exists, a verification link will be sent"}
        )
    
    if user.is_verified:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Email already verified"}
        )
    
    # Generate new verification code
    verification_code = generate_verification_code()
    user.verification_code = verification_code
    db.commit()
    
    # Send verification email
    try:
        await send_verification_email(user.email, verification_code)
    except Exception as e:
        print(f"Error sending verification email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error sending verification email"
        )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Verification email sent"}
    )

# Get current user profile
@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
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
        raise HTTPException(status_code=404, detail="Activity not found")
    
    for key, value in activity.dict(exclude_unset=True).items():
        setattr(db_activity, key, value)
    
    db.commit()
    db.refresh(db_activity)
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
        raise HTTPException(status_code=404, detail="Activity not found")
    
    db.delete(db_activity)
    db.commit()
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
    return db_tag

@app.get("/tags/", response_model=List[schemas.Tag])
def read_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    tags = db.query(models.Tag).offset(skip).limit(limit).all()
    return tags 