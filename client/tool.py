import os
import time
import hashlib
import configparser
import requests
import json


class Tool(object):
    config = configparser.ConfigParser()
    config.read('config.cfg')
    host = config.get('http_server', 'host', fallback='127.0.0.1')
    port = config.get('http_server', 'port', fallback=8888)
    token = config.get('http_server', 'token', fallback='')

    @staticmethod
    def get_md5(string):
        h1 = hashlib.md5()
        h1.update(string.encode(encoding='utf-8'))
        return h1.hexdigest()

    @staticmethod
    def sync_faces():
        sync_time = Tool.config.getfloat('http_server', 'sync_time', fallback='0.0')
        try:
            timestamp = time.time()
            data = {
                "timestamp": timestamp,
                "token": Tool.get_md5(Tool.token + str(timestamp)),
                'sync_time': sync_time
            }
            r = requests.post('{}:{}/list'.format(Tool.host, Tool.port), data=data)
            result = json.loads(r.text)
            if result['code'] == 0:
                faces = result['data']
                for face in faces:
                    Tool.download_face(face)
            if result['code'] in [0, 1]:
                Tool.config.set('http_server', 'sync_time', str(timestamp))
                fp = open('config.cfg', 'w')
                Tool.config.write(fp)
                fp.close()
        except Exception as e:
            print(e)
            pass

    @staticmethod
    def download_face(face):
        name = face["username"]
        face_name = face["face"]
        res = requests.get('{}:{}/static/{}'.format(Tool.host, Tool.port, face_name))
        if not os.path.exists("faces"):
            os.mkdir("faces")
        path = "faces" + os.sep + name
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path + os.sep + 'desc.txt', 'w') as f:
            f.write(face['desc'])
        with open(path + os.sep + str(time.time()) + ".png", 'wb') as f:
            f.write(res.content)
