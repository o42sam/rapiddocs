from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
import ssl


class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None
    connected: bool = False


db = Database()


async def connect_to_mongo():
    """Connect to MongoDB Atlas"""
    try:
        print(f"Attempting to connect to MongoDB...")
        print(f"Database name: {settings.MONGODB_DB_NAME}")

        # Connect to MongoDB Atlas
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=30000
        )

        # Test the connection
        print("Testing connection with ping...")
        await db.client.admin.command('ping')

        db.db = db.client[settings.MONGODB_DB_NAME]
        db.connected = True
        print(f"✓ Connected to MongoDB: {settings.MONGODB_DB_NAME}")

        # List collections to verify database access
        collections = await db.db.list_collection_names()
        print(f"✓ Available collections: {collections if collections else 'None (new database)'}")

    except Exception as e:
        import traceback
        print(f"✗ MongoDB connection failed!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Traceback:")
        traceback.print_exc()
        print("⚠ Application will run in demo mode (without persistence)")
        db.connected = False


async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if not db.connected:
        raise Exception("Database not connected. Please check MongoDB configuration.")
    return db.db
