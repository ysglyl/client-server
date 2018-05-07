from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'tb_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    ip = db.Column(db.String(32))
    cmd = db.Column(db.String(32))

    def __init__(self, username, ip, cmd):
        self.username = username
        self.ip = ip
        self.cmd = cmd

    def __repr__(self):
        return '<User %r>' % self.username


class Face(db.Model):
    __tablename__ = 'tb_face'

    id = db.Column(db.Integer, primary_key=True)
    face = db.Column(db.String(120), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tb_user.id'))

    def __init__(self, face, user_id):
        self.face = face
        self.user_id = user_id

    def __repr__(self):
        return '<Face %r>' % self.face
