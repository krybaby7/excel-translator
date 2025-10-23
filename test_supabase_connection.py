"""
Test Supabase Connection
Run this script to verify your Supabase setup is working correctly
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test Supabase connection and configuration"""
    print("=" * 60)
    print("Testing Supabase Connection")
    print("=" * 60)

    # Get credentials
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")

    if not url or not key:
        print("❌ ERROR: Missing environment variables")
        print("   Make sure SUPABASE_URL and SUPABASE_SERVICE_KEY are set in .env")
        return False

    print(f"\n✓ Found credentials")
    print(f"  URL: {url}")
    print(f"  Key: {key[:20]}...")

    try:
        # Create client
        print("\n→ Creating Supabase client...")
        supabase: Client = create_client(url, key)
        print("✓ Client created successfully")

        # Test database connection
        print("\n→ Testing database connection...")
        result = supabase.table("translation_jobs").select("count").execute()
        print(f"✓ Database connected! Found {len(result.data)} jobs")

        # Test storage connection
        print("\n→ Testing storage connection...")
        buckets = supabase.storage.list_buckets()
        print(f"✓ Storage connected! Found {len(buckets)} buckets:")
        for bucket in buckets:
            print(f"  - {bucket.name}")

        # Check if excel-files bucket exists
        excel_bucket = next((b for b in buckets if b.name == "excel-files"), None)
        if excel_bucket:
            print("✓ 'excel-files' bucket found!")
        else:
            print("⚠ WARNING: 'excel-files' bucket not found!")
            print("  You need to create it in Supabase dashboard")

        # Test inserting a record
        print("\n→ Testing database write...")
        test_job = {
            "original_filename": "test.xlsx",
            "source_lang": "en",
            "target_lang": "fr",
            "status": "pending",
            "progress_message": "Test connection"
        }
        insert_result = supabase.table("translation_jobs").insert(test_job).execute()
        test_id = insert_result.data[0]['id']
        print(f"✓ Successfully created test job: {test_id}")

        # Clean up test record
        print("→ Cleaning up test job...")
        supabase.table("translation_jobs").delete().eq("id", test_id).execute()
        print("✓ Test job deleted")

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour Supabase setup is working correctly.")
        print("You can now proceed with deployment to Vercel.")
        return True

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has correct credentials")
        print("2. Verify you ran the supabase-schema.sql in SQL Editor")
        print("3. Make sure you created the 'excel-files' storage bucket")
        print("4. Check your internet connection")
        return False

if __name__ == "__main__":
    # Check if python-dotenv is installed
    try:
        import dotenv
    except ImportError:
        print("Installing python-dotenv...")
        os.system("pip install python-dotenv")
        from dotenv import load_dotenv
        load_dotenv()

    # Check if supabase is installed
    try:
        import supabase
    except ImportError:
        print("Installing supabase...")
        os.system("pip install supabase")
        from supabase import create_client, Client

    test_connection()
