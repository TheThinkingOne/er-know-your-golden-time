import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ER_API_KEY: str = os.getenv("ER_API_KEY", "")
    ER_API_BASE_URL: str = "https://open-api.bser.io"


settings = Settings()