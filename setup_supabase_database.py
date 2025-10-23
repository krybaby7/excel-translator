"""
Setup Supabase Database
This script executes the SQL schema on your Supabase database
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Execute the SQL schema on Supabase database"""
    print("=" * 60)
    print("Setting up Supabase Database")
    print("=" * 60)

    # Get credentials
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")

    if not url or not key:
        print("❌ ERROR: Missing environment variables")
        print("   Make sure SUPABASE_URL and SUPABASE_SERVICE_KEY are set in .env")
        return False

    print(f"\n✓ Using Supabase URL: {url}")

    try:
        # Create client
        print("\n→ Creating Supabase client...")
        supabase: Client = create_client(url, key)
        print("✓ Client created")

        # Read SQL schema
        print("\n→ Reading SQL schema...")
        with open('supabase-schema.sql', 'r') as f:
            sql_schema = f.read()
        print("✓ Schema loaded")

        # Execute SQL (note: Supabase Python client doesn't support raw SQL execution directly)
        # We'll use the REST API to execute SQL via RPC
        print("\n→ Executing SQL schema...")
        print("\n⚠️  NOTE: The Supabase Python client doesn't support direct SQL execution.")
        print("   You need to run the SQL manually in the Supabase Dashboard.")
        print("\n📋 Instructions:")
        print("   1. Go to https://supabase.com/dashboard")
        print("   2. Select your project: ExcelTranslate")
        print("   3. Click 'SQL Editor' in the left sidebar")
        print("   4. Click 'New Query'")
        print("   5. Copy the contents of 'supabase-schema.sql'")
        print("   6. Paste into the SQL Editor")
        print("   7. Click 'Run' (bottom right)")
        print("\n   Or simply run the content below:")
        print("=" * 60)
        print(sql_schema)
        print("=" * 60)

        print("\n→ Testing database connection...")
        # Test if we can access the database (after manual schema creation)
        try:
            result = supabase.table("translation_jobs").select("count").execute()
            print(f"✓ Database connected! Table exists with {len(result.data)} records")
            return True
        except Exception as e:
            print(f"⚠️  Table not found: {str(e)}")
            print("   Please run the SQL schema manually (see instructions above)")
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    setup_database()
