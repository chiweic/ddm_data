import logging

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

logging.basicConfig(level=logging.INFO)

# dev_ddm
# pKVHkpH2NRc4hSSF
db_username='dev_ddm'
db_password='pKVHkpH2NRc4hSSF'
uri = "mongodb+srv://{}:{}@cluster0.o0rhbep.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0".format(db_username,db_password)

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    #client.admin.command('ping')
    #print("Pinged your deployment. You successfully connected to MongoDB!")
    # create a collection
    
    db = client['ddm']
    db.create_collection('events')
    client.close()

except Exception as e:
    print(e)


