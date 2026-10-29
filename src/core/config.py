from pathlib import Path
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer


#pemakaian nanti tinggal tulis aja mau import apaan

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv('.env')

#load dari environment
DATABASE_URL = os.getenv('DATABASE_URL')
ALAMAT_STORAGE = os.getenv('ALAMAT_STORAGE')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl='login')
MAKSIMUM_WAKTU_DEVICE = 90
ESP_32_API_KEY = 'Dwl33cLcAzlX_LyNMkF-cQ'
