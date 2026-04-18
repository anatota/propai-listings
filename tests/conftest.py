import os

# Set a dummy DATABASE_URL before app.database is imported,
# so the production engine can be created without a real .env file.
os.environ.setdefault("DATABASE_URL", "sqlite:///./unused.db")
