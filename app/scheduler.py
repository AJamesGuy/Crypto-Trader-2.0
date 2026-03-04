from apscheduler.schedulers.background import BackgroundScheduler
from .services.coingecko_service import update_market_data
import logging
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def schedule_market_data_update(app):
    with app.app_context():
        update_market_data(limit=200, vs_currency='usd') # coingecko api call in app context

def start_scheduler(app):
    """Initialize and start the background scheduler for market data updates""" 
    scheduler.add_job(
        func=schedule_market_data_update,
        args=[app],
        trigger='date',
        run_date=None,  # Run immediately on startup
        id='initial_market_data_update',
        name='Initial CoinGecko Market Data Update',
        replace_existing=True,
    )
    # Add job to update market data every 15 seconds
    scheduler.add_job(
        func=schedule_market_data_update,
        args=[app],
        trigger="interval",
        minutes=1,
        id="update_market_data",
        name="Update CoinGecko Market Data",
        replace_existing=True,
    )

    def handle_job_error(event):
        if event.exception:
            logger.error(f"Error in scheduled job '{event.job_id}': {event.exception}")
        else:
            logger.info(f"Scheduled job '{event.job_id}' completed successfully")
    
    scheduler.add_listener(handle_job_error, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
    scheduler.start()

    logger.info("Background scheduler started - market data will update every 15 minutes")