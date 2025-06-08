#!/usr/bin/env python3
"""
Database setup script for PlantCare AI application.
This script creates the database and all necessary tables.
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from database import Base, create_tables
from config import DATABASE_URL

def create_database():
    """Create the database if it doesn't exist"""
    
    # Extract database name from URL
    db_name = DATABASE_URL.split('/')[-1]
    base_url = DATABASE_URL.rsplit('/', 1)[0]
    
    print(f"Setting up database: {db_name}")
    
    try:
        # Connect to PostgreSQL server (without specific database)
        engine = create_engine(f"{base_url}/postgres")
        
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_name}
            )
            
            if not result.fetchone():
                # Create database
                conn.execute(text("COMMIT"))  # End any existing transaction
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"✅ Database '{db_name}' created successfully")
            else:
                print(f"✅ Database '{db_name}' already exists")
                
    except OperationalError as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        print("Make sure PostgreSQL is running and credentials are correct")
        return False
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False
    
    return True

def setup_tables():
    """Create all application tables"""
    
    try:
        print("Creating application tables...")
        create_tables()
        print("✅ All tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def create_sample_data():
    """Create sample data for testing (optional)"""
    
    try:
        from sqlalchemy.orm import sessionmaker
        from database import User, engine
        from auth import get_password_hash
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            # Create admin user
            admin_user = User(
                email="admin@plantcare.ai",
                username="admin",
                full_name="Admin User",
                hashed_password=get_password_hash("admin123"),
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ Admin user created (username: admin, password: admin123)")
        else:
            print("✅ Admin user already exists")
            
        # Create test user
        test_user = db.query(User).filter(User.username == "testuser").first()
        
        if not test_user:
            test_user = User(
                email="test@plantcare.ai",
                username="testuser",
                full_name="Test User",
                hashed_password=get_password_hash("test123")
            )
            db.add(test_user)
            db.commit()
            print("✅ Test user created (username: testuser, password: test123)")
        else:
            print("✅ Test user already exists")
            
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def main():
    """Main setup function"""
    
    print("🌿 PlantCare AI Database Setup")
    print("=" * 40)
    
    # Step 1: Create database
    if not create_database():
        sys.exit(1)
    
    # Step 2: Create tables
    if not setup_tables():
        sys.exit(1)
    
    # Step 3: Create sample data (optional)
    create_sample = input("\nCreate sample users? (y/N): ").lower().strip()
    if create_sample in ['y', 'yes']:
        create_sample_data()
    
    print("\n✅ Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start the application: python main.py")
    print("3. Open your browser to: http://localhost:8000")
    
    if create_sample in ['y', 'yes']:
        print("\nSample users created:")
        print("- Admin: username=admin, password=admin123")
        print("- Test: username=testuser, password=test123")

if __name__ == "__main__":
    main() 