import os
import time
import cv2
from haarcascade_detective import HaarcascadeDetective

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QIcon, QImage, QPixmap

from tool import Tool


class AddFaceDialog(QDialog):
    def __init__(self, image):
        super(AddFaceDialog, self).__init__()
        self.setFixedSize(300, 275)
        self.setWindowIcon(QIcon('icons/add.png'))
        self.setWindowTitle('添加')
        lbl_face = QLabel('人脸', self)
        lbl_face.setGeometry(10, 22, 50, 26)
        lbl_face.setAlignment(Qt.AlignCenter)

        lbl_name = QLabel('名称', self)
        lbl_name.setGeometry(10, 80, 50, 26)
        lbl_name.setAlignment(Qt.AlignCenter)
        self.le_name = QLineEdit(self)
        self.le_name.setGeometry(70, 80, 200, 26)
        lbl_desc = QLabel('欢迎语', self)
        lbl_desc.setGeometry(10, 116, 50, 26)
        lbl_desc.setAlignment(Qt.AlignCenter)
        self.le_desc = QLineEdit(self)
        self.le_desc.setGeometry(70, 116, 200, 26)
        lbl_ip = QLabel('展位IP', self)
        lbl_ip.setGeometry(10, 152, 50, 26)
        lbl_ip.setAlignment(Qt.AlignCenter)
        self.le_ip = QLineEdit(self)
        self.le_ip.setGeometry(70, 152, 200, 26)
        lbl_cmd = QLabel('指令', self)
        lbl_cmd.setGeometry(10, 188, 50, 26)
        lbl_cmd.setAlignment(Qt.AlignCenter)
        self.le_cmd = QLineEdit(self)
        self.le_cmd.setGeometry(70, 188, 200, 26)

        self.btn_save = QPushButton(self)
        self.btn_save.setText('保存')
        self.btn_save.setGeometry(10, 234, 280, 30)
        self.btn_save.clicked.connect(self.save)

        self.cache_faces = {}
        self.face = None

        faces = HaarcascadeDetective().get_face_classifier().get_faces(image)
        index = 0
        for face in faces:
            viewer_face = QPushButton(self)
            viewer_face.setGeometry(70 * (index + 1), 10, 60, 60)
            viewer_face.setIconSize(QSize(56, 56))
            img = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            image = QImage(img, img.shape[1], img.shape[0], img.shape[1] * 3, QImage.Format_RGB888)
            pix_map = QPixmap.fromImage(image)
            viewer_face.setIcon(QIcon(pix_map))
            viewer_face.clicked.connect(self.select_face)
            self.cache_faces[viewer_face] = face
            if index == 0:
                self.face = face
                viewer_face.setStyleSheet('border-color: rgb(255, 0, 0);border-style: outset;border-width: 2px;')
            index += 1
            if index > 2:
                break

        if index == 0:
            lbl_message = QLabel(self)
            lbl_message.setText('未检测到人脸信息');
            lbl_message.setGeometry(70, 22, 100, 26)
            self.btn_save.setDisabled(True)

    def select_face(self):
        sender = self.sender()
        for btn in self.cache_faces:
            btn.setStyleSheet('border-style: none')
        sender.setStyleSheet("border-color: rgb(255, 0, 0);border-style: outset;border-width: 2px;")
        self.face = self.cache_faces[btn]

    def save(self):
        if self.face is None:
            return
        name = self.le_name.text()
        if name.strip(' ') == '':
            self.btn_save.setText('请输入名称')
            self.le_name.setFocus()
            return
        desc = self.le_desc.text()
        if desc.strip(' ') == '':
            self.btn_save.setText('请输入欢迎语')
            self.le_desc.setFocus()
            return
        ip = self.le_ip.text()
        if ip.strip(' ') == '':
            self.btn_save.setText('请输入IP')
            self.le_ip.setFocus()
            return
        cmd = self.le_cmd.text()
        if cmd.strip(' ') == '':
            self.btn_save.setText('请输入指令')
            self.le_cmd.setFocus()
            return
        if not os.path.exists('faces/{}'.format(name)):
            os.mkdir('faces/{}'.format(name))
        face_name = 'faces/{}/{}.png'.format(name, time.time())
        cv2.imwrite(face_name, self.face)
        result = Tool.upload(name, desc, ip, cmd, face_name)
        if result:
            self.close()
        else:
            self.btn_save.setText('上传识别，请检查网络连接')
