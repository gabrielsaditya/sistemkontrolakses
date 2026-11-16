import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv('.env')

FASTAPI_URL = os.getenv('URL_API')
API_KEY = os.getenv('API_KEY')
