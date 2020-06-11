# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fgo/ui/AiScenariosDialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AiScenarioDialog(object):
    def setupUi(self, AiScenarioDialog):
        AiScenarioDialog.setObjectName("AiScenarioDialog")
        AiScenarioDialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(AiScenarioDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(AiScenarioDialog)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_3 = QtWidgets.QFrame(self.frame)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.frame_3)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.lwAvailable = QtWidgets.QListWidget(self.frame_3)
        self.lwAvailable.setObjectName("lwAvailable")
        self.verticalLayout_2.addWidget(self.lwAvailable)
        self.pbAdd = QtWidgets.QPushButton(self.frame_3)
        self.pbAdd.setObjectName("pbAdd")
        self.verticalLayout_2.addWidget(self.pbAdd)
        self.horizontalLayout.addWidget(self.frame_3)
        self.frame_2 = QtWidgets.QFrame(self.frame)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        self.lwActive = QtWidgets.QListWidget(self.frame_2)
        self.lwActive.setObjectName("lwActive")
        self.verticalLayout_3.addWidget(self.lwActive)
        self.pbRemove = QtWidgets.QPushButton(self.frame_2)
        self.pbRemove.setObjectName("pbRemove")
        self.verticalLayout_3.addWidget(self.pbRemove)
        self.horizontalLayout.addWidget(self.frame_2)
        self.verticalLayout.addWidget(self.frame)
        self.buttonBox = QtWidgets.QDialogButtonBox(AiScenarioDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AiScenarioDialog)
        self.buttonBox.accepted.connect(AiScenarioDialog.accept)
        self.buttonBox.rejected.connect(AiScenarioDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AiScenarioDialog)

    def retranslateUi(self, AiScenarioDialog):
        _translate = QtCore.QCoreApplication.translate
        AiScenarioDialog.setWindowTitle(_translate("AiScenarioDialog", "Select AI Scenarios"))
        self.label.setText(_translate("AiScenarioDialog", "Available"))
        self.pbAdd.setText(_translate("AiScenarioDialog", "Add"))
        self.label_2.setText(_translate("AiScenarioDialog", "Active"))
        self.pbRemove.setText(_translate("AiScenarioDialog", "Remove"))
