from app import create_app
from app.database.connection import init_db
import os

app = create_app()

if __name__ == "__main__":
    # Initialize DB if it doesn't exist (simplistic check)
    if not os.path.exists('wellbeing.db'):
        print("Initializing database...")
        init_db()
    app.run(debug=True)
