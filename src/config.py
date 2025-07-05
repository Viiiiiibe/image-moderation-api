import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

SIGHTENGINE_API_URL = "https://api.sightengine.com/1.0/check.json"
SIGHTENGINE_API_USER = os.getenv("SIGHTENGINE_API_USER")
SIGHTENGINE_API_SECRET = os.getenv("SIGHTENGINE_API_SECRET")
THRESHOLD = 0.7  # Порог для всех проверок
