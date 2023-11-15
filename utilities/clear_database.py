from pymongo import MongoClient

# Connect to your MongoDB server
client = MongoClient('mongodb://localhost:27017')

# Select the database and collection
db = client['urlresults']
collection = db['results']

# Delete all entries in the collection
collection.delete_many({})

# Close the MongoDB connection
client.close()