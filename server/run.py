import os
import shutil
import time
import json
from flask import Flask, render_template, request
from db.dbhelper import User, Face, db
from db.dao import FaceDao
from tool import Tool
from haarcascade_detective import HaarcascadeDetective

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
app.config.from_pyfile('db/db.cfg')

db.init_app(app)


@app.route('/')
@app.route('/index')
def page_index():
    users = FaceDao.list_user()
    return render_template('index.html', users=users)


@app.route('/upload', methods=['POST'], endpoint='upload')
def upload_detect():
    try:
        file_detect = request.files['file_detect']
        path = os.path.split(os.path.realpath(__file__))[
                   0] + os.path.sep + "static" + os.path.sep + "upload"
        if not os.path.exists(path):
            os.mkdir(path)
        face_path = path + os.path.sep + file_detect.filename
        file_detect.save(face_path)
        face_list = HaarcascadeDetective().get_face_classifier().get_faces(face_path)
        if len(face_list) > 0:
            return json.dumps({"code": 0, "data": face_list})
        else:
            return json.dumps({"code": 1})
    except Exception as e:
        return json.dumps({"code": -1})


@app.route('/websave', methods=['POST', 'GET'], endpoint='websave')
def websave_face():
    try:
        name = request.form['username']
        ip = request.form['ip']
        cmd = request.form['cmd']
        desc = request.form['desc']
        face_name = request.form['face']
        cur_path, _ = os.path.split(os.path.realpath(__file__))
        face_src = cur_path + os.sep + "static" + os.sep + "upload" + os.sep + face_name
        path_dst = cur_path + os.sep + "static" + os.sep + "faces" + os.sep + name
        if not os.path.exists(path_dst):
            os.mkdir(path_dst)
        shutil.move(face_src, path_dst + os.sep + face_name)
        user_id = FaceDao.add_user(User(username=name, ip=ip, cmd=cmd, desc=desc))
        if user_id != -1:
            face_relative_path = 'faces/' + name + '/' + face_name
            FaceDao.add_face(Face(face=face_relative_path, time_point=time.time(), user_id=user_id))
        return json.dumps({"code": 0})
    except Exception as e:
        return json.dumps({"code": -1})


@app.route('/save', methods=['POST'])
def save_face():
    try:
        timestamp = request.form['timestamp']
        token = request.form['token']
        if token != Tool.get_md5(app.config.get('TOKEN') + str(timestamp)):
            return 'Fail'
        name = request.form['name']
        desc = request.form['desc']
        ip = request.form['ip']
        cmd = request.form['cmd']
        face_img = request.files['face']
        path = os.path.split(os.path.realpath(__file__))[
                   0] + os.path.sep + "static" + os.path.sep + "faces" + os.path.sep + name
        if not os.path.exists(path):
            os.mkdir(path)
        face_path = path + os.path.sep + face_img.filename
        face_img.save(face_path)
        user_id = FaceDao.add_user(User(username=name, ip=ip, cmd=cmd, desc=desc))
        if user_id != -1:
            face_relative_path = 'faces/' + name + '/' + face_img.filename
            FaceDao.add_face(Face(face=face_relative_path, time_point=time.time(), user_id=user_id))
        return json.dumps({"code": 0})
    except Exception as e:
        return json.dumps({"code": -1})


@app.route('/list', methods=['POST'])
def sync_list():
    try:
        timestamp = request.form['timestamp']
        token = request.form['token']
        if token != Tool.get_md5(app.config.get('TOKEN') + str(timestamp)):
            return 'Fail'
        sync_time = request.form['sync_time']
        faces = FaceDao.list_new_faces(sync_time)
        if len(faces) > 0:
            return json.dumps({'code': 0, 'data': faces})
        else:
            return json.dumps({'code': 1})
    except Exception as e:
        return json.dumps({'code': -1})


@app.before_first_request
def init_db():
    db.create_all()


@app.errorhandler(404)
def handler_error_404(error):
    return '404', 404


@app.errorhandler(500)
def handler_error_500(error):
    return '500', 500


if __name__ == '__main__':
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'))
