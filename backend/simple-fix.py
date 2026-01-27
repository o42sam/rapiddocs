import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    # Your actual MongoDB connection string
    client = AsyncIOMotorClient('mongodb+srv://samscarfaceegbo:G7a1n14G7@cluster1.vehwbxh.mongodb.net/?appName=Cluster1')
    db = client['docgen_prod']

    result = await db.admins.update_one(
        {'username': 'psycho_ceo'},
        {'$set': {'is_superuser': True, 'permissions': ['*']}}
    )

    if result.modified_count > 0:
        print('✅ Successfully updated psycho_ceo to superuser!')
    else:
        admin = await db.admins.find_one({'username': 'psycho_ceo'})
        if admin and admin.get('is_superuser'):
            print('✅ psycho_ceo is already a superuser!')
        else:
            print('❌ Failed to update')

    client.close()

asyncio.run(main())