from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
JWT_SECRET = os.getenv("JWT_SECRET")

if any(x is None for x in (DATABASE_URL, REDIS_URL, JWT_SECRET)):
    raise RuntimeError("Missing environmental variable from .env")