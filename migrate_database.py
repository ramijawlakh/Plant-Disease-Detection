#!/usr/bin/env python3
"""
Database migration script to add profile_picture column to User table.
Run this if you're getting 500 errors after adding the profile feature.
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError

# Use the same DATABASE_URL as database.py
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Charbel2004@localhost:5432/fastapi_db")

def migrate_database():
    """Add profile_picture column to users table"""
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if profile_picture column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'profile_picture'
            """))
            
            if result.fetchone():
                print("✅ profile_picture column already exists")
                return True
            
            # Add the profile_picture column
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN profile_picture VARCHAR NULL
            """))
            
            conn.commit()
            print("✅ Successfully added profile_picture column to users table")
            return True
            
    except OperationalError as e:
        print(f"❌ Database connection error: {e}")
        print("Make sure PostgreSQL is running and the database exists")
        return False
    except ProgrammingError as e:
        print(f"❌ SQL error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main migration function"""
    
    print("🌿 PlantCare AI Database Migration")
    print("=" * 40)
    print("Adding profile_picture column to users table...")
    print(f"Using database: {DATABASE_URL}")
    
    if migrate_database():
        print("\n✅ Migration completed successfully!")
        print("You can now login and use the profile features.")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 