from motor.motor_asyncio import AsyncIOMotorClient
import asyncio


async def connect_to_mongo(url):
    client = AsyncIOMotorClient(url)
    admin_db = client['admin']
    return client, admin_db


async def list_users(admin_db):
    try:
        users = await admin_db.command("usersInfo")
        for user in users['users']:
            print(f"User: {user['user']} - Roles: {user['roles']}")
    except Exception as e:
        print(f"Failed to list users: {e}")


async def main(url):
    try:
        client, admin_db = await connect_to_mongo(url)
        await list_users(admin_db)
        client.close()
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

if __name__ == "__main__":
    # url_local = "mongodb://admin:yourpassword@localhost:27017"
    url_atlas = "mongodb+srv://admin:SN76K70DR5M87vs1@eim-be-dev.ahlma5d.mongodb.net"
    # asyncio.run(main(url_local))
    asyncio.run(main(url_atlas))
