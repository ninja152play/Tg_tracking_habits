import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
BASE_DIR = Path(__file__).parent.parent
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30
ALGORITHM = "RS256"