from dotenv import load_dotenv, find_dotenv
from app.core.app_builder import create_app

load_dotenv(find_dotenv())
app = create_app()
