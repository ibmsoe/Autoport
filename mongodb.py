from pymongo import MongoClient
from log import logger
import globals

class MongoDB:
    # Autoport knowledge-base is maintained in monogodb.
    # This class provides an interface to interact with the
    # database.

    # Initializes an instance of MongoDB class
    def __init__(self):
        try:
            self._conn = MongoClient(globals.connectionURL, int(globals.connectionPort))
            self._conn[globals.dbName].authenticate(globals.dbUsername, globals.dbPassword)
            self._db = self._conn[globals.dbName]
        except Exception as e:
            logger.warning("Unable to connect to database with " \
            "connectionUrl=%s due to error=%s" %(globals.connectionURL, str(e)))
            globals.enableKnowledgeBase = False
            return

    # Method allows to insert a record into mongodb
    def insertRecord(self, dict_data):
        self._db[globals.dbCollectionName].insert(dict_data)

    # Method allows to query a record from mongodb
    def queryForRecord(self, dict_data):
        return self._db[globals.dbCollectionName].find(dict_data)

    # Method allows to update a record in mongodb
    def updateRecord(self,key,dict_data):
        self._db[globals.dbCollectionName].update(key,dict_data)
