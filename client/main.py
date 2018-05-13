import os
import cv2
import time
import numpy as np
from threading import Thread
import collections

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QLabel, QFrame
from PyQt5.QtGui import QIcon, QImage, QPixmap

from haarcascade_detective import HaarcascadeDetective

from tool import Tool


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.camera = None
        self.playing = False
        self.frames = collections.deque(maxlen=33)
        self.flag_recognize = False
        self.face_names = []
        self.face_desc = {}
        self.model = None

        self.recognized_faces = {}

        self.lbl_info = None
        self.lbl_viewer = None
        self.init_ui()
        self.refresh_model()
        self.exit_time = 0

    def init_ui(self):
        screen = QDesktopWidget().availableGeometry()
        self.setGeometry(screen)
        self.setWindowIcon(QIcon('icons/icon.png'))
        self.setWindowTitle('客户端')
        self.lbl_viewer = QLabel(self)
        self.lbl_viewer.setAlignment(Qt.AlignCenter)
        self.lbl_viewer.setGeometry(self.geometry())
        self.lbl_viewer.setFrameShape(QFrame.StyledPanel)
        self.start_play()

    def start_play(self):
        self.playing = True
        self.camera = cv2.VideoCapture(0)
        play_thread = Thread(target=self.play)
        play_thread.start()
        recognize_thread = Thread(target=self.recognize)
        recognize_thread.start()

    def play(self):
        while self.camera.isOpened():
            if not self.playing:
                break
            ret, frame = self.camera.read()
            if ret:
                self.frames.appendleft(frame.copy())
                faces = self.recognized_faces.copy()
                for name in faces:
                    x, y, w, h = faces[name]
                    if Tool.config.getboolean('recognize', 'show_rectangle', fallback=True):
                        cv2.rectangle(frame, (x, y), (x + w, y + h),
                                      eval(Tool.config.get('recognize', 'color_rectangle', fallback=(255, 0, 0))), 1,
                                      cv2.LINE_AA)
                    if Tool.config.getboolean('recognize', 'show_name', fallback=True):
                        cv2.putText(frame, name, (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                    eval(Tool.config.get('recognize', 'color_name', fallback=(255, 0, 0))), 2)
                    if Tool.config.getboolean('recognize', 'show_desc', fallback=True):
                        desc = self.face_desc.get(name, '')
                        if desc:
                            cv2.putText(frame, desc, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                        eval(Tool.config.get('recognize', 'color_desc', fallback=(255, 0, 0))), 2)
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = QImage(img, img.shape[1], img.shape[0], img.shape[1] * 3, QImage.Format_RGB888)
                pix_map = QPixmap.fromImage(image)
                pix_map = pix_map.scaled(self.lbl_viewer.width(), self.lbl_viewer.height(), Qt.KeepAspectRatio)
                self.lbl_viewer.setPixmap(pix_map)

        self.lbl_viewer.clear()
        self.camera.release()

    def recognize(self):
        classifier = HaarcascadeDetective().get_face_classifier()
        while self.playing:
            if len(self.frames) == 0:
                continue
            frame = self.frames.pop()
            faces = classifier.get_faces_position(frame)
            self.recognized_faces.clear()
            for (x, y, w, h) in faces:
                face = frame[y:y + h, x:x + w]
                if self.model is not None:
                    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                    params = self.model.predict(gray)
                    if params[1] <= Tool.config.getint('recognize', 'threshold', fallback=50):
                        self.recognized_faces[self.face_names[params[0]]] = (x, y, w, h)
                    else:
                        self.recognized_faces['Unknown'] = (x, y, w, h)
                else:
                    self.recognized_faces['Unknown'] = (x, y, w, h)

    def stop_play(self):
        self.playing = False

    def load_faces(self):
        y, X = [], []
        faces_root = os.listdir('faces')
        for dir in faces_root:
            if os.path.isdir('faces{}{}'.format(os.sep, dir)):
                if dir not in self.face_names:
                    self.face_names.append(dir)
                faces = os.listdir('faces{}{}'.format(os.sep, dir))
                for face in faces:
                    if face.endswith('.png'):
                        y.append(self.face_names.index(dir))
                        im = cv2.imread('faces{}{}{}{}'.format(os.sep, dir, os.sep, face), 0)
                        X.append(np.asarray(im, dtype=np.uint8))
                    elif face.endswith('.txt'):
                        with open('faces{}{}{}desc.txt'.format(os.sep, dir, os.sep), 'r') as f:
                            self.face_desc[dir] = f.readline()
        if len(X) != 0 and len(y) != 0:
            self.model = cv2.face.LBPHFaceRecognizer_create()
            self.model.train(np.asarray(X), np.asarray(y, dtype=np.int32))

    def refresh_model(self):
        Tool.sync_faces()
        self.load_faces()

    def closeEvent(self, *args, **kwargs):
        self.playing = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            cur_time = time.time()
            if cur_time - self.exit_time < 0.5:
                self.close()
                self.app.exit(0)
            else:
                self.exit_time = cur_time
