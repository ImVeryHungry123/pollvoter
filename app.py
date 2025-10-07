from app import create_app, db
from dotenv import load_dotenv
app = create_app()
load_dotenv()
with app.app_context():
    db.create_all()
if __name__ == "__main__":
    app.run(debug=True)