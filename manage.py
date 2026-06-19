from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

def init_db():
    """Ensures that the database tables are created."""
    with app.app_context():
        try:
            # This will create tables if they don't exist
            db.create_all()
            print("Database tables verified/created successfully.")
        except Exception as e:
            print(f"Error initializing database: {e}")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
