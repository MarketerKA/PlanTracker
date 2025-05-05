from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db
import logging
from ..telegram_bot import send_notification, format_time


ACTIVITY_NOT_FOUND = "Activity not found"


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

activity_router = APIRouter(prefix="/activities", tags=["activities"])


# Calculate elapsed time between timer start and now
def calculate_elapsed_time(activity):
    if activity.timer_status == "running" and activity.last_timer_start:
        # Calculate time since timer was started
        elapsed = datetime.now() - activity.last_timer_start
        # Convert to seconds
        return int(elapsed.total_seconds())
    return 0


# Activity endpoints


@activity_router.post("/", response_model=schemas.Activity)
def create_activity(
    activity: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    # Get tags from activity data
    tag_names = activity.tags

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

    logger.info(
        f"Activity created by user: {current_user.email}, activity ID: {db_activity.id}"
    )
    return db_activity


@activity_router.get("/", response_model=List[schemas.Activity])
def read_activities(
    skip: int = 0,
    limit: int = 15,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    # Base query for user's activities
    query = db.query(models.Activity).filter(models.Activity.user_id == current_user.id)

    # Filter by tag if provided
    if tag:
        query = query.join(models.Activity.tags).filter(models.Tag.name == tag)

    # Get activities with pagination
    activities = (
        query.order_by(models.Activity.start_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Update timer status for running timers
    for activity in activities:
        if activity.timer_status == "running":
            elapsed = calculate_elapsed_time(activity)
            activity.recorded_time += elapsed

    logger.info(
        f"Activities retrieved for user: {current_user.email}, count: {len(activities)}"
    )
    return activities


@activity_router.get("/{activity_id}", response_model=schemas.Activity)
def read_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    # Get activity
    db_activity = (
        db.query(models.Activity)
        .filter(
            models.Activity.id == activity_id,
            models.Activity.user_id == current_user.id,
        )
        .first()
    )

    if not db_activity:
        logger.warning(
            f"Activity {activity_id} not found for user {current_user.email}"
        )
        raise HTTPException(status_code=404, detail=ACTIVITY_NOT_FOUND)

    # Update recorded time if timer is running
    if db_activity.timer_status == "running" and db_activity.last_timer_start:
        elapsed = calculate_elapsed_time(db_activity)
        db_activity.recorded_time += elapsed
        db_activity.last_timer_start = datetime.now()
        db.commit()

    logger.info(f"Activity {activity_id} retrieved by user: {current_user.email}")
    return db_activity


@activity_router.put("/{activity_id}", response_model=schemas.Activity)
def update_activity(
    activity_id: int,
    activity: schemas.ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    db_activity = (
        db.query(models.Activity)
        .filter(
            models.Activity.id == activity_id,
            models.Activity.user_id == current_user.id,
        )
        .first()
    )
    if not db_activity:
        logger.warning(
            f"Activity update failed: Activity {activity_id} not found for "
            f"user {current_user.email}"
        )
        raise HTTPException(status_code=404, detail=ACTIVITY_NOT_FOUND)

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


@activity_router.delete("/{activity_id}")
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    db_activity = (
        db.query(models.Activity)
        .filter(
            models.Activity.id == activity_id,
            models.Activity.user_id == current_user.id,
        )
        .first()
    )
    if not db_activity:
        logger.warning(
            f"Activity deletion failed: Activity {activity_id} not found for "
            f"user {current_user.email}"
        )
        raise HTTPException(status_code=404, detail=ACTIVITY_NOT_FOUND)

    db.delete(db_activity)
    db.commit()
    logger.info(f"Activity {activity_id} deleted by user: {current_user.email}")
    return {"message": "Activity deleted successfully"}


# Timer functionality endpoints


async def handle_timer_start(activity, current_time, user):
    """Handle timer start action."""
    if activity.timer_status == "running":
        logger.info(f"Timer already running for activity {activity.id}")
        return False

    activity.timer_status = "running"
    activity.last_timer_start = current_time

    if user.telegram_chat_id:
        await send_notification(user.id, f"▶️ Timer started for task: {activity.title}")
    logger.info(f"Timer started for activity {activity.id} by user {user.email}")
    return True


async def handle_timer_pause(activity, current_time, user):
    """Handle timer pause action."""
    if activity.timer_status != "running":
        logger.warning(f"Cannot pause: Timer not running for activity {activity.id}")
        raise HTTPException(status_code=400, detail="Timer not running")

    elapsed = calculate_elapsed_time(activity)
    activity.recorded_time += elapsed
    activity.timer_status = "paused"
    activity.last_timer_start = None

    if user.telegram_chat_id:
        await send_notification(
            user.id,
            f"⏸️ Timer paused for task: {activity.title}\n"
            f"Saved time: {format_time(activity.recorded_time)}",
        )
    logger.info(f"Timer paused for activity {activity.id} by user {user.email}")
    return True


async def handle_timer_stop(activity, current_time, user):
    """Handle timer stop action."""
    if activity.timer_status == "stopped":
        logger.warning(f"Timer already stopped for activity {activity.id}")
        return False

    if activity.timer_status == "running":
        elapsed = calculate_elapsed_time(activity)
        activity.recorded_time += elapsed

    activity.timer_status = "stopped"
    activity.last_timer_start = None

    if user.telegram_chat_id:
        await send_notification(
            user.id,
            f"⏹️ Timer stopped for task: {activity.title}\n"
            f"Total time: {format_time(activity.recorded_time)}",
        )
    logger.info(f"Timer stopped for activity {activity.id} by user {user.email}")
    return True


def handle_timer_save(activity, current_time):
    """Handle timer save action."""
    if activity.timer_status == "running":
        elapsed = calculate_elapsed_time(activity)
        activity.recorded_time += elapsed
        activity.last_timer_start = current_time

    logger.info(f"Timer saved for activity {activity.id}")
    return True


@activity_router.post("/{activity_id}/timer", response_model=schemas.Activity)
async def activity_timer(
    activity_id: int,
    timer_action: schemas.TimerAction,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    # Get activity
    db_activity = (
        db.query(models.Activity)
        .filter(
            models.Activity.id == activity_id,
            models.Activity.user_id == current_user.id,
        )
        .first()
    )

    if not db_activity:
        logger.warning(
            f"Timer action failed: Activity {activity_id} not found for "
            f"user {current_user.email}"
        )
        raise HTTPException(status_code=404, detail=ACTIVITY_NOT_FOUND)

    action = timer_action.action.lower()
    current_time = datetime.now()

    # Handle timer actions using action handlers
    action_handlers = {
        "start": handle_timer_start,
        "pause": handle_timer_pause,
        "stop": handle_timer_stop,
        "save": handle_timer_save,
    }

    if action not in action_handlers:
        logger.warning(f"Invalid timer action: {action} for activity {activity_id}")
        raise HTTPException(status_code=400, detail="Invalid timer action")

    # Execute the appropriate handler
    if action == "save":
        handle_timer_save(db_activity, current_time)
    else:
        await action_handlers[action](db_activity, current_time, current_user)

    # Save changes to database
    db.commit()
    db.refresh(db_activity)
    return db_activity
