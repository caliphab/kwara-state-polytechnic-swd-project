from dotenv import load_dotenv
load_dotenv()


from app import create_app
from config import app_env


app = create_app(app_env)

if __name__ == "__main__":
    app.run()