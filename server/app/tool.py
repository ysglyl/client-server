import hashlib


class Tool(object):

    @staticmethod
    def get_md5(string):
        h1 = hashlib.md5()
        h1.update(string.encode(encoding='utf-8'))
        return h1.hexdigest()
