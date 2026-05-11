from app import create_app, db
from app.models import PredictionHistory

app = create_app()

def init_database():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database initialized successfully.")

if __name__ == '__main__':
    init_database()
