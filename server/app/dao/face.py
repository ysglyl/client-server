from app.db.dbhelper import db, User, Face


class FaceDao(object):

    @staticmethod
    def add_user(user):
        try:
            db.session.add(user)
            db.session.commit()
            return user.id
        except Exception as e:
            print(e)
            return -1

    @staticmethod
    def add_face(face):
        try:
            db.session.add(face)
            db.session.commit()
            return 0
        except Exception as e:
            print(e)
            return -1
