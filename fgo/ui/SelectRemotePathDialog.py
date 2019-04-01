# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fgo/ui/SelectRemotePathDialog.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SelectRemotePathDialog(object):
    def setupUi(self, SelectRemotePathDialog):
        SelectRemotePathDialog.setObjectName("SelectRemotePathDialog")
        SelectRemotePathDialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(SelectRemotePathDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelCurrentPath = QtWidgets.QLabel(SelectRemotePathDialog)
        self.labelCurrentPath.setObjectName("labelCurrentPath")
        self.verticalLayout.addWidget(self.labelCurrentPath)
        self.listWidget = QtWidgets.QListWidget(SelectRemotePathDialog)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.frame = QtWidgets.QFrame(SelectRemotePathDialog)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pbSelect = QtWidgets.QPushButton(self.frame)
        self.pbSelect.setObjectName("pbSelect")
        self.horizontalLayout.addWidget(self.pbSelect)
        self.pbSelectNone = QtWidgets.QPushButton(self.frame)
        self.pbSelectNone.setObjectName("pbSelectNone")
        self.horizontalLayout.addWidget(self.pbSelectNone)
        self.pbCancel = QtWidgets.QPushButton(self.frame)
        self.pbCancel.setObjectName("pbCancel")
        self.horizontalLayout.addWidget(self.pbCancel)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(SelectRemotePathDialog)
        QtCore.QMetaObject.connectSlotsByName(SelectRemotePathDialog)

    def retranslateUi(self, SelectRemotePathDialog):
        _translate = QtCore.QCoreApplication.translate
        SelectRemotePathDialog.setWindowTitle(_translate("SelectRemotePathDialog", "Select Remote Path"))
        self.labelCurrentPath.setText(_translate("SelectRemotePathDialog", "TextLabel"))
        self.pbSelect.setText(_translate("SelectRemotePathDialog", "Select"))
        self.pbSelectNone.setText(_translate("SelectRemotePathDialog", "Select None"))
        self.pbCancel.setText(_translate("SelectRemotePathDialog", "Cancel"))


