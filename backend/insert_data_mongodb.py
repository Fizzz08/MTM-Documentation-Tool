import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to MongoDB
mongo_url = os.environ.get('MONGO_URL', "mongodb://localhost:27017") #Get MongoDB URL from environment or default to localhost
client = MongoClient(mongo_url)
db = client["healthcare"]
collection = db["Dataset1"]

json_filepath = 'output/newDataset.json'

try:
    with open(json_filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # If data is a list, use it directly
    documents = data if isinstance(data, list) else list(data.values())

    if documents:
        collection.insert_many(documents)
        print(f"✅ Inserted {len(documents)} documents into MongoDB.")
    else:
        print("No data found to insert.")

except Exception as e:
    print(f"Error inserting data into MongoDB: {e}")

client.close()
