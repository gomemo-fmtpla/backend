from app.database import db
from fastapi import Depends
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from app.database.db import get_db
from app.usecases.note.note import delete_old_notes
import logging

logger = logging.getLogger(__name__)

def cleanup_old_notes(db: Session):
    logger.info("Starting cleanup of old notes...")
    
    result = delete_old_notes(db)
    
    if result["success"]:
        logger.info(f"Successfully deleted {result['deleted_count']} old notes")
        if result["errors"]:
            logger.warning("Some errors occurred during cleanup:")
            for error in result["errors"]:
                logger.warning(error)
    else:
        logger.error("Failed to cleanup old notes:")
        for error in result["errors"]:
            logger.error(error)

def init_cleanup_scheduler():
    scheduler = BackgroundScheduler()
    
    # Run cleanup task every day at 3 AM
    scheduler.add_job(
        cleanup_old_notes,
        'cron',
        hour=3,
        minute=0,
        args=[next(get_db())]
    )
    
    # Activate this for testing:
    # scheduler.add_job(
    #     cleanup_old_notes,
    #     'interval',
    #     minutes=1,  # Run every minute for testing
    #     args=[db],
    #     id='cleanup_old_notes'
    # )
    
    
    scheduler.start()
    logger.info("Cleanup scheduler initialized")