"""App configuration — use environment variables for real values, never hardcode secrets."""

import os

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://localhost/setu")
