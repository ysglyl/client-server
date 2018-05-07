import os
from flask import Blueprint, render_template, request, current_app
from app.db.dbhelper import User, Face
from app.dao.face import FaceDao
from tool import Tool

face = Blueprint('face', __name__, template_folder='templates', static_folder='static')


@face.route('/save', methods=['POST'])
def save_face():
    try:
        timestamp = request.form['timestamp']
        token = request.form['token']
        if token != Tool.get_md5(current_app.config.get('TOKEN') + str(timestamp)):
            return 'Fail'
        name = request.form['name']
        ip = request.form['ip']
        cmd = request.form['cmd']
        face_img = request.files['face']
        path = os.path.split(os.path.realpath(__file__))[
                   0] + os.path.sep + "static" + os.path.sep + "face" + os.path.sep + "faces" + os.path.sep + name
        if not os.path.exists(path):
            os.mkdir(path)
        face_path = path + os.path.sep + face_img.filename
        face_img.save(face_path)
        user_id = FaceDao.add_user(User(username=name, ip=ip, cmd=cmd))
        FaceDao.add_face(Face(face=face_path, user_id=user_id))
        return 'success'
    except Exception as e:
        print(e)
        return 'error'


@face.route('/list', methods=['POST'])
def sync_list():
    try:
        timestamp = request.form['timestamp']
        token = request.form['token']
        if token != Tool.get_md5(current_app.config.get('TOKEN') + str(timestamp)):
            return 'Fail'
        sync_time = request.form['sync_time']

        return 'success'
    except Exception as e:
        print(e)
        return 'error'
