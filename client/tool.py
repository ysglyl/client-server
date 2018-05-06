import time
import hashlib
import configparser
import requests
import json


class Tool():
    config = configparser.ConfigParser()
    config.read('config.cfg')

    @staticmethod
    def get_win_width():
        w = Tool.config.getint('dimension', 'width', fallback=800)
        return w if w >= 640 else 640

    @staticmethod
    def get_win_height():
        h = Tool.config.getint('dimension', 'height', fallback=600)
        return h if h >= 480 else 480

    @staticmethod
    def get_md5(string):
        h1 = hashlib.md5()
        h1.update(string.encode(encoding='utf-8'))
        return h1.hexdigest()

    @staticmethod
    def upload(name, ip, cmd, face):
        host = Tool.config.get('http_server', 'host', fallback='127.0.0.1')
        port = Tool.config.get('http_server', 'port', fallback=8888)
        token = Tool.config.get('http_server', 'token', fallback='')
        try:
            timestamp = time.time()
            files = {'face': open(face, 'rb')}
            data = {
                "timestamp": timestamp,
                "token": Tool.get_md5(token + str(timestamp)),
                "name": name,
                "ip": ip,
                "cmd": cmd
            }
            r = requests.post('{}:{}/face/save'.format(host, port), data=data, files=files)
            if r.text == 'success':
                return True
            else:
                return False
        except Exception as e:
            print(e)
            pass

    @staticmethod
    def sync_faces():
        sync_time = Tool.config.getfloat('http_server', 'sync_time', fallback='0.0')
        host = Tool.config.get('http_server', 'host', fallback='127.0.0.1')
        port = Tool.config.get('http_server', 'port', fallback=8888)
        token = Tool.config.get('http_server', 'token', fallback='')
        try:
            timestamp = time.time()
            data = {
                "timestamp": timestamp,
                "token": Tool.get_md5(token + str(timestamp)),
                'sync_time': sync_time
            }
            r = requests.post('{}:{}/face/list'.format(host, port), data=data)
            faces = json.loads(r.text)
            for face in faces:
                Tool.download_face(face)
            Tool.config.set('http_server', 'sync_time', timestamp)
            fp = open('config.cfg', 'wb')
            Tool.config.write(fp)
            fp.close()
        except Exception as e:
            print(e)
            pass

    @staticmethod
    def download_face(face):
        print(face)
