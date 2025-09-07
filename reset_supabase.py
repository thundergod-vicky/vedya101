#!/usr/bin/env python3
"""
Supabase Database Reset Script
This script safely resets the database tables for a fresh setup.
"""

import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def reset_supabase_database():
    """Reset database tables safely."""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Connect to Supabase PostgreSQL
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to Supabase PostgreSQL successfully")
        
        print("🧹 Cleaning up existing tables...")
        
        # Drop tables in reverse dependency order
        tables_to_drop = [
            'chat_messages',
            'chat_conversations', 
            'kanban_tasks',
            'agent_runs',
            'user_progress',
            'lessons',
            'courses',
            'learning_plans',
            'users'
        ]
        
        for table in tables_to_drop:
            try:
                await conn.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                print(f"✅ Dropped table: {table}")
            except Exception as e:
                print(f"⚠️  Could not drop {table}: {e}")
        
        await conn.close()
        print("\n🎉 Database reset completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database reset failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧹 Resetting VEDYA database...")
    success = asyncio.run(reset_supabase_database())
    
    if success:
        print("\n✅ Database is ready for fresh setup!")
        print("Run 'python setup_supabase.py' to create tables again.")
    else:
        print("\n❌ Database reset failed.")
