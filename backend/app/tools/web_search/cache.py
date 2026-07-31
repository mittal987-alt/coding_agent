import time


class SearchCache:

    def __init__(self):

        self.cache = {}

    def get(

        self,

        key,

    ):

        value = self.cache.get(key)

        if value is None:

            return None

        expires, data = value

        if expires < time.time():

            del self.cache[key]

            return None

        return data

    def put(

        self,

        key,

        value,

        ttl=3600,

    ):

        self.cache[key] = (

            time.time() + ttl,

            value,

        )