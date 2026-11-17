import os
import psycopg
from dotenv import load_dotenv

def get_connection():
    
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        raise SystemExit("Missing DATABASE_URL in .env")
    
    return psycopg.connect(database_url)