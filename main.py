from dotenv import load_dotenv
from app import create_app
from config import app_env


load_dotenv()

app = create_app(app_env)

if __name__ == "__main__":
    app.run()