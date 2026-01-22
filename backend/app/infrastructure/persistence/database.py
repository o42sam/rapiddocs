from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.server_api import ServerApi
from app.config import settings
import ssl
import certifi


class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None
    connected: bool = False


db = Database()


async def connect_to_mongo():
    """Connect to MongoDB Atlas"""
    # Check if MongoDB is explicitly disabled or URL is empty
    if settings.DISABLE_MONGODB or not settings.MONGODB_URL:
        print("⚠ MongoDB is disabled or not configured")
        print("⚠ Application will run in demo mode (without persistence)")
        db.connected = False
        return

    try:
        print(f"Attempting to connect to MongoDB...")
        print(f"Database name: {settings.MONGODB_DB_NAME}")

        # Check if using mongodb+srv:// format
        is_srv = settings.MONGODB_URL.startswith("mongodb+srv://")
        print(f"Using SRV connection: {is_srv}")
        print(f"Python SSL version: {ssl.OPENSSL_VERSION}")
        print(f"Certifi CA bundle location: {certifi.where()}")

        # MongoDB Atlas connection with Stable API v1
        # This is required by newer MongoDB Atlas clusters
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            server_api=ServerApi('1'),
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
