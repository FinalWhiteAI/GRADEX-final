from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("lkk"*100)
    print(SUPABASE_URL)
    raise Exception("Supabase credentials missing in .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
