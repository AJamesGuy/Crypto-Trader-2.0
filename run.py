from app.models import db
from app import create_app
from app.scheduler import start_scheduler

app = create_app('DevelopmentConfig')

with app.app_context():
    db.drop_all()  # Drop existing tables for a clean slate
    db.create_all()
    start_scheduler(app)  # Start the background scheduler for market data updates

if __name__ == "__main__":
    app.run(debug=True)