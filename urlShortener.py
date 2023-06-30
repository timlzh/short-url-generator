import re
import base62
import pymongo

class InvalidUrlError(BaseException):
    pass

def validate_url(url: str) -> bool:
    return (re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url) is not None)

class UrlShortener:
    def __init__(self, host: str, port: int, db_name: str, collection_name: str, login: bool = False, user: str = None, password: str = None):
        self.client = pymongo.MongoClient(host, port)
        
        if login:
            self.client.admin.authenticate(user, password, mechanism='SCRAM-SHA-1')
        
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.conter = self.db['counter']
        if self.conter.count_documents({}) == 0:
            self.conter.insert_one({'_id': 'counter', 'seq': 0})
    
    def __get_next_id(self) -> int:
        return self.conter.find_one_and_update({'_id': 'counter'}, {'$inc': {'seq': 1}})['seq']
    
    def get_url(self, short: str) -> str:
        id = base62.decode(short)
        if self.collection.count_documents({'_id': id}) != 0:
            return self.collection.find_one({'_id': id})['url']
        else:
            return None
    
    def shorten_url(self, url: str) -> str:
        if not validate_url(url):
            raise InvalidUrlError
        
        if self.collection.count_documents({'url': url}) != 0:
            return self.collection.find_one({'url': url})['short']
        else:
            id = self.__get_next_id()
            short = base62.encode(id)
            self.collection.insert_one({'_id': id, 'url': url, 'short': short})
            return short 