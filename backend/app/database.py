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
        # Connect to MongoDB Atlas
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=30000
        )
        # Test the connection
        await db.client.admin.command('ping')
        db.db = db.client[settings.MONGODB_DB_NAME]
        db.connected = True
        print(f"✓ Connected to MongoDB: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        print(f"⚠ MongoDB connection failed: {str(e)}")
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
