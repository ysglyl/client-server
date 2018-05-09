import os
import shutil
import time
import json
from flask import Blueprint, render_template, request, current_app
from app.db.dbhelper import User, Face
from app.dao.face import FaceDao
from app.tool import Tool
from app.haarcascade_detective import HaarcascadeDetective

face = Blueprint('face', __name__, template_folder='templates', static_folder='static')


@face.route('/index')
@face.route('/list')
def page_index():
    users = FaceDao.list_user()
    return render_template('face/index.html', users=users)


@face.route('/upload', methods=['POST'], endpoint='upload')
def upload_detect():
    try:
        file_detect = request.files['file_detect']
        path = os.path.split(os.path.realpath(__file__))[
                   0] + os.path.sep + "static" + os.path.sep + "face" + os.path.sep + "upload"
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
        print(e)
        return json.dumps({"code": -1})


@face.route('/websave', methods=['POST', 'GET'], endpoint='websave')
def websave_face():
    try:
        name = request.form['username']
        ip = request.form['ip']
        cmd = request.form['cmd']
        desc = request.form['desc']
        face_name = request.form['face']
        cur_path, _ = os.path.split(os.path.realpath(__file__))
        face_src = cur_path + os.sep + "static" + os.sep + "face" + os.sep + "upload" + os.sep + face_name
        path_dst = cur_path + os.sep + "static" + os.sep + "face" + os.sep + "faces" + os.sep + name
        if not os.path.exists(path_dst):
            os.mkdir(path_dst)
        shutil.move(face_src, path_dst + os.sep + face_name)
        user_id = FaceDao.add_user(User(username=name, ip=ip, cmd=cmd, desc=desc))
        if user_id != -1:
            face_relative_path = 'face/faces/' + name + '/' + face_name
            FaceDao.add_face(Face(face=face_relative_path, time_point=time.time(), user_id=user_id))
        return json.dumps({"code": 0})
    except Exception as e:
        print(e)
        return json.dumps({"code": -1})


@face.route('/save', methods=['POST'])
def save_face():
    try:
        timestamp = request.form['timestamp']
        token = request.form['token']
        if token != Tool.get_md5(current_app.config.get('TOKEN') + str(timestamp)):
            return 'Fail'
        name = request.form['name']
        desc = request.form['desc']
        ip = request.form['ip']
        cmd = request.form['cmd']
        face_img = request.files['face']
        path = os.path.split(os.path.realpath(__file__))[
                   0] + os.path.sep + "static" + os.path.sep + "face" + os.path.sep + "faces" + os.path.sep + name
        if not os.path.exists(path):
            os.mkdir(path)
        face_path = path + os.path.sep + face_img.filename
        face_img.save(face_path)
        user_id = FaceDao.add_user(User(username=name, ip=ip, cmd=cmd, desc=desc))
        if user_id != -1:
            face_relative_path = 'face/faces/' + name + '/' + face_img.filename
            FaceDao.add_face(Face(face=face_relative_path, time_point=time.time(), user_id=user_id))
        return json.dumps({"code": 0})
    except Exception as e:
        print(e)
        return json.dumps({"code": -1})


@face.route('/list', methods=['POST'])
def sync_list():
    try:
        timestamp = request.form['timestamp']
        token = request.form['token']
        if token != Tool.get_md5(current_app.config.get('TOKEN') + str(timestamp)):
            return 'Fail'
        sync_time = request.form['sync_time']
        faces = FaceDao.list_new_faces(sync_time)
        if len(faces) > 0:
            return json.dumps({'code': 0, 'data': faces})
        else:
            return json.dumps({'code': 1})
    except Exception as e:
        print(e)
        return json.dumps({'code': -1})
