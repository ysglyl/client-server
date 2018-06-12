from db.dbhelper import db, User, Face


class FaceDao(object):

    @staticmethod
    def add_user(user):
        try:
            exist = User.query.filter(User.username == user.username).first()
            if exist is not None:
                User.query.filter(User.username == user.username).update({User.ip: user.ip, User.cmd: user.cmd})
                db.session.commit()
                return exist.id
            else:
                db.session.add(user)
                db.session.commit()
                return user.id
        except Exception as e:
            return -1

    @staticmethod
    def add_face(face):
        try:
            db.session.add(face)
            db.session.commit()
            return 0
        except Exception as e:
            return -1

    @staticmethod
    def query_by_name(name):
        try:
            user = User.query.filter(User.username == name).first()
            return user
        except Exception as e:
            return None

    @staticmethod
    def list_user():
        user_list = []
        users = User.query.all()
        for user in users:
            user_dict = {"id": user.id, "username": user.username, "ip": user.ip, "cmd": user.cmd, "desc": user.desc}
            face = user.faces.order_by(Face.id.desc()).first()
            user_dict["face"] = face.face
            user_list.append(user_dict)
        return user_list

    @staticmethod
    def list_new_faces(time_point):
        face_list = []
        users = User.query.all()
        for user in users:
            faces = user.faces.filter(Face.time_point > time_point).all()
            for face in faces:
                face_dict = {"username": user.username, "desc": user.desc}
                face_dict["face"] = face.face
                face_list.append(face_dict)
        return face_list
