import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# Fetch Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Fetch individual database components
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Construct the DATABASE_URL for SQLAlchemy
if all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = None

# Fail fast if critical environment variables are missing
if not DATABASE_URL:
    raise ValueError("CRITICAL ERROR: One or more Database environment variables are missing in the .env file.")

if not GROQ_API_KEY:
    raise ValueError("CRITICAL ERROR: GROQ_API_KEY is missing in the .env file.")

# Helper function to safely print masked keys for debugging
def get_masked_key(key: str, visible_chars: int = 4) -> str:
    if not key or len(key) <= visible_chars * 2:
        return "***"
    return f"{key[:visible_chars]}...{key[-visible_chars:]}"

if __name__ == "__main__":
    # Test block: Run this file directly to verify it loads correctly
    print("--- Config Test ---")
    
    # Masking the DB URL carefully so we don't expose the password in logs
    safe_db_url = f"postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print(f"Database URL constructed: {safe_db_url}")
    print(f"Groq API Key loaded: {get_masked_key(GROQ_API_KEY, 4)}")
    print("Configuration loaded successfully!")