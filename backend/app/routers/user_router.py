from fastapi import APIRouter, Depends, HTTPException, status
from email_validator import validate_email, EmailNotValidError
import logging
from .. import schemas, models, auth
from sqlalchemy.orm import Session
from ..database import get_db
from datetime import timedelta
from .. import config


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


user_router = APIRouter(prefix="/users", tags=["users"])


# Validate email with email-validator library
def validate_email_address(email: str) -> bool:
    try:
        # Validate and get normalized result
        valid = validate_email(email, check_deliverability=True)

        logger.info(f"Email validated successfully: {valid.normalized}")
        return True
    except EmailNotValidError as e:
        logger.warning(f"Email validation failed: {str(e)}")
        return False


@user_router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Log the request
    logger.info(f"User registration attempt: {user.email}")

    # Check if user with this email already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        logger.warning(f"Registration failed: Email already registered: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Validate email with email-validator library
    if not validate_email_address(user.email):
        logger.warning(f"Registration failed: Invalid email address: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address. Please provide a valid email.",
        )

    # Hash the password
    hashed_password = auth.get_password_hash(user.password)

    # Create new user
    db_user = models.User(email=user.email, hashed_password=hashed_password)

    # Save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    logger.info(f"User registered successfully: {user.email}")
    return db_user


# JSON-based login endpoint for frontend applications
@user_router.post("/login", response_model=schemas.Token)
async def login_json(login_data: schemas.UserCreate, db: Session = Depends(get_db)):
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
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    logger.info(f"Login successful for user: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}


# Get current user profile


@user_router.get("/me", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(auth.get_current_active_user),
):
    logger.info(f"Profile accessed by user: {current_user.email}")
    return current_user


@user_router.get("/me/telegram-status")
async def get_telegram_status(
    current_user: models.User = Depends(auth.get_current_active_user),
):
    return {
        "is_linked": bool(current_user.telegram_chat_id),
        "telegram_chat_id": current_user.telegram_chat_id,
    }


@user_router.delete("/me/telegram", response_model=dict)
async def unlink_telegram(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    if not current_user.telegram_chat_id:
        raise HTTPException(status_code=400, detail="Telegram account not linked")

    current_user.telegram_chat_id = None
    db.commit()

    return {"message": "Telegram account unlinked successfully"}
