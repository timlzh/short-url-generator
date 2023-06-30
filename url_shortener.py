"""
@Author: Timlzh <2921349622@qq.com>
"""
import re

import pymongo

import base62

InvalidUrlError = ValueError('Invalid URL')


def validate_url(url: str) -> bool:
    """validate_url

    Args:
        url (str): url to validate

    Returns:
        bool: True if url is valid, else False
    """
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.match(pattern, url)


class UrlShortener:
    """
    UrlShortener
    """

    def __init__(self, host: tuple = ('localhost', 27017),
                 login: bool = False, user: str = None, password: str = None):
        self.client = pymongo.MongoClient(*host)
        if login:
            self.client.admin.authenticate(
                user, password, mechanism='SCRAM-SHA-1')

        self.database = self.client['shortUrlDB']
        self.collection = self.database['shorturls']
        self.conter = self.database['counter']
        if self.conter.count_documents({}) == 0:
            self.conter.insert_one({'_id': 'counter', 'seq': 0})

    def __get_next_id(self) -> int:
        return self.conter.find_one_and_update({'_id': 'counter'}, {'$inc': {'seq': 1}})['seq']

    def get_url(self, short: str) -> str:
        """get_url

        Args:
            short (str): short url

        Returns:
            str: original url
        """
        url_id = base62.decode(short)
        if self.collection.count_documents({'_id': url_id}) != 0:
            return self.collection.find_one({'_id': url_id})['url']
        return None

    def shorten_url(self, url: str) -> str:
        """shorten a url

        Args:
            url (str): url to shorten

        Raises:
            InvalidUrlError: if url is invalid

        Returns:
            str: short url
        """
        if not validate_url(url):
            raise InvalidUrlError

        if self.collection.count_documents({'url': url}) != 0:
            return self.collection.find_one({'url': url})['short']
        url_id = self.__get_next_id()
        short = base62.encode(url_id)
        self.collection.insert_one({'_id': url_id, 'url': url, 'short': short})
        return short
