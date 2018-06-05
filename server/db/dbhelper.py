from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'tb_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    ip = db.Column(db.String(32))
    cmd = db.Column(db.String(32))
    desc = db.Column(db.String(256))
    faces = db.relationship('Face', backref='user', lazy='dynamic')

    def __init__(self, username, ip, cmd, desc):
        self.username = username
        self.ip = ip
        self.cmd = cmd
        self.desc = desc

    def __repr__(self):
        return str({"id": self.id, "username": self.username, "ip": self.ip, "cmd": self.cmd, "desc": self.desc,
                    "faces": str(self.faces)})


class Face(db.Model):
    __tablename__ = 'tb_face'

    id = db.Column(db.Integer, primary_key=True)
    face = db.Column(db.String(120), unique=True)
    time_point = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('tb_user.id'))

    def __init__(self, face, time_point, user_id):
        self.face = face
        self.time_point = time_point
        self.user_id = user_id

    def __repr__(self):
        return str({"id": self.id, "face": self.face})
