"""
config.py - Loads Supabase credentials from the .env file.

The real values live only in .env (which .gitignore keeps off GitHub).
"""

import os

from dotenv import load_dotenv

load_dotenv()  # reads .env in the current folder into environment variables

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
