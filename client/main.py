import os
import cv2
import numpy as np
from threading import Thread
import collections

from PyQt5.QtCore import QRect, Qt, QSize
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QLabel, QPushButton, QCheckBox, QFrame
from PyQt5.QtGui import QIcon, QFont, QImage, QPixmap

from dialogs import AddFaceDialog
from haarcascade_detective import HaarcascadeDetective

from tool import Tool


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.camera = None
        self.playing = False
        self.frames = None
        self.cache_frame = None
        self.capture_frames = collections.deque(maxlen=3)
        self.flag_recognize = False
        self.face_names = []
        self.model = None

        self.recognized_faces = {}

        self.lbl_viewer = None
        self.btn_open_camera = None
        self.cb_recognize = None
        self.btn_capture = None
        self.btn_close_camera = None
        self.btn_capture_1 = None
        self.btn_capture_2 = None
        self.btn_capture_3 = None

        self.init_ui()
        Tool.sync_faces()
        self.load_faces()

    def init_ui(self):
        self.setFixedSize(Tool.get_win_width(), Tool.get_win_height())
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowIcon(QIcon('icons/icon.png'))
        self.setWindowTitle('客户端')

        self.lbl_viewer = QLabel(self)
        self.lbl_viewer.setGeometry(QRect(10, 10, Tool.get_win_width() - 130, Tool.get_win_height() - 20))
        self.lbl_viewer.setText('没有图像')
        font = QFont()
        font.setPointSize(20)
        self.lbl_viewer.setFont(font)
        self.lbl_viewer.setAlignment(Qt.AlignCenter)
        self.lbl_viewer.setFrameShape(QFrame.StyledPanel)

        self.btn_open_camera = QPushButton(self)
        self.btn_open_camera.setGeometry(QRect(Tool.get_win_width() - 110, 10, 100, 26))
        self.btn_open_camera.setText('打开摄像头')
        self.btn_open_camera.clicked.connect(self.btn_click)

        self.btn_close_camera = QPushButton(self)
        self.btn_close_camera.setGeometry(QRect(Tool.get_win_width() - 110, 46, 100, 26))
        self.btn_close_camera.setText('关闭摄像头')
        self.btn_close_camera.setDisabled(True)
        self.btn_close_camera.clicked.connect(self.btn_click)

        self.cb_recognize = QCheckBox(self)
        self.cb_recognize.setText('启动识别')
        self.cb_recognize.setDisabled(True)
        self.cb_recognize.setGeometry(QRect(Tool.get_win_width() - 108, 82, 100, 26))
        self.cb_recognize.clicked.connect(self.cb_click)

        self.btn_capture = QPushButton(self)
        self.btn_capture.setGeometry(QRect(Tool.get_win_width() - 110, Tool.get_win_height() - 366, 100, 26))
        self.btn_capture.setText('截屏')
        self.btn_capture.setDisabled(True)
        self.btn_capture.clicked.connect(self.btn_click)

        self.btn_capture_1 = QPushButton(self)
        self.btn_capture_1.setGeometry(QRect(Tool.get_win_width() - 110, Tool.get_win_height() - 330, 100, 100))
        self.btn_capture_1.setIconSize(QSize(98, 98))
        self.btn_capture_1.setDisabled(True)
        self.btn_capture_1.clicked.connect(self.btn_click)
        self.btn_capture_2 = QPushButton(self)
        self.btn_capture_2.setGeometry(QRect(Tool.get_win_width() - 110, Tool.get_win_height() - 220, 100, 100))
        self.btn_capture_2.setIconSize(QSize(98, 98))
        self.btn_capture_2.setDisabled(True)
        self.btn_capture_2.clicked.connect(self.btn_click)
        self.btn_capture_3 = QPushButton(self)
        self.btn_capture_3.setGeometry(QRect(Tool.get_win_width() - 110, Tool.get_win_height() - 110, 100, 100))
        self.btn_capture_3.setIconSize(QSize(98, 98))
        self.btn_capture_3.setDisabled(True)
        self.btn_capture_3.clicked.connect(self.btn_click)

    def btn_click(self):
        btn = self.sender()
        if btn == self.btn_open_camera:
            self.camera = cv2.VideoCapture(0)
            self.frames = collections.deque(maxlen=33)
            self.start_play()
        elif btn == self.btn_close_camera:
            self.stop_play()
        elif btn == self.btn_capture:
            try:
                self.capture_frames.appendleft(self.cache_frame)
                num = len(self.capture_frames)
                if num > 0:
                    self.show_capture(self.btn_capture_1, self.capture_frames[0])
                    self.btn_capture_1.setDisabled(False)
                if num > 1:
                    self.show_capture(self.btn_capture_2, self.capture_frames[1])
                    self.btn_capture_2.setDisabled(False)
                if num > 2:
                    self.show_capture(self.btn_capture_3, self.capture_frames[2])
                    self.btn_capture_3.setDisabled(False)
            except ValueError as ve:
                pass
        elif btn == self.btn_capture_1:
            AddFaceDialog(self.capture_frames[0]).exec()
        elif btn == self.btn_capture_2:
            AddFaceDialog(self.capture_frames[1]).exec()
        elif btn == self.btn_capture_3:
            AddFaceDialog(self.capture_frames[2]).exec()

    def cb_click(self):
        cb = self.sender()
        if cb == self.cb_recognize:
            if cb.isChecked():
                self.flag_recognize = True
            else:
                self.flag_recognize = False

    def change_widget_disabled(self, status):
        self.btn_open_camera.setDisabled(not status[0])
        self.btn_close_camera.setDisabled(not status[1])
        self.cb_recognize.setDisabled(not status[2])
        self.btn_capture.setDisabled(not status[3])

    def start_play(self):
        self.playing = True
        self.change_widget_disabled((False, True, True, True))
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
                self.cache_frame = frame.copy()
                self.frames.appendleft(frame.copy())
                if self.flag_recognize:
                    for name in self.recognized_faces:
                        x, y, w, h = self.recognized_faces[name]
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1, cv2.LINE_AA)
                        cv2.putText(frame, name, (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = QImage(img, img.shape[1], img.shape[0], img.shape[1] * 3, QImage.Format_RGB888)
                pix_map = QPixmap.fromImage(image)
                pix_map = pix_map.scaled(Tool.get_win_width() - 130, Tool.get_win_height() - 20, Qt.KeepAspectRatio)
                self.lbl_viewer.setPixmap(pix_map)

        self.lbl_viewer.clear()
        self.camera.release()

    def recognize(self):
        classifier = HaarcascadeDetective().get_face_classifier()
        while self.playing:
            if len(self.frames) == 0:
                continue
            frame = self.frames.pop()
            if self.flag_recognize:
                faces = classifier.get_faces_position(frame)
                self.recognized_faces.clear()
                for (x, y, w, h) in faces:
                    face = frame[y:y + h, x:x + w]
                    if self.model is not None:
                        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                        params = self.model.predict(gray)
                        self.recognized_faces[self.face_names[params[0]]] = (x, y, w, h)
                    else:
                        self.recognized_faces['Unknown'] = (x, y, w, h)

    def stop_play(self):
        self.playing = False
        self.change_widget_disabled((True, False, False, False))

    def show_capture(self, viewer, image):
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(img, img.shape[1], img.shape[0], img.shape[1] * 3, QImage.Format_RGB888)
        pix_map = QPixmap.fromImage(image)
        icon = QIcon(pix_map)
        viewer.setIcon(icon)

    def load_faces(self):
        y, X = [], []
        faces_root = os.listdir('faces')
        for dir in faces_root:
            if os.path.isdir('faces/{}'.format(dir)):
                faces = os.listdir('faces/{}'.format(dir))
                for face in faces:
                    if dir not in self.face_names:
                        self.face_names.append(dir)
                    y.append(self.face_names.index(dir))
                    im = cv2.imread('faces/{}/{}'.format(dir, face), 0)
                    X.append(np.asarray(im, dtype=np.uint8))
        if len(X) != 0 and len(y) != 0:
            self.model = cv2.face.LBPHFaceRecognizer_create()
            self.model.train(np.asarray(X), np.asarray(y, dtype=np.int32))

    def closeEvent(self, *args, **kwargs):
        self.playing = False
