import os
from tool import Tool
from flask import Flask, request

app = Flask(__name__)
app.config.from_pyfile('config.cfg')


@app.route('/')
@app.route('/index')
def index():
    return 'Index'


@app.route('/face/save', methods=['POST'])
def save_face():
    try:
        timestamp = request.form['timestamp']
        token = request.form['token']
        if token != Tool.get_md5(app.config.get('TOKEN') + str(timestamp)):
            return 'Fail'
        name = request.form['name']
        ip = request.form['ip']
        cmd = request.form['cmd']
        face = request.files['face']
        path = os.path.split(os.path.realpath(__file__))[0] + os.path.sep + "faces" + os.path.sep + name
        if not os.path.exists(path):
            os.mkdir(path)
        face.save(path + os.path.sep + face.filename)
        return 'success'
    except Exception as e:
        print(e)
        return 'error'


@app.route('/face/list', methods=['POST'])
def sync_list():
    try:
        timestamp = request.form['timestamp']
        token = request.form['token']
        if token != Tool.get_md5(app.config.get('TOKEN') + str(timestamp)):
            return 'Fail'
        sync_time = request.form['sync_time']

        return 'success'
    except Exception as e:
        print(e)
        return 'error'


if __name__ == '__main__':
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'), debug=True)
