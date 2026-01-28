import os

from dotenv import load_dotenv


# Loads `.env` if present (not committed). This is safe even if the file doesn't exist.
load_dotenv()

def _getenv(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)

# Example: ENV=dev
# ENV: str = _getenv("ENV")