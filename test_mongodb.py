from pymongo import MongoClient
import certifi

MONGO_URI = "mongodb+srv://indhiyas2007_db_user:NadAi2007Test@cluster0.vxqcqon.mongodb.net/?appName=Cluster0"

try:
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000
    )

    client.admin.command("ping")

    print("MongoDB Connected Successfully!")

except Exception as e:
    print("\nMongoDB Connection Error:\n")
    print(e)