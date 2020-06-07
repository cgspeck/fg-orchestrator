# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fgo\ui\SelectParkingLocationDialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dlgSelectParkingLocation(object):
    def setupUi(self, dlgSelectParkingLocation):
        dlgSelectParkingLocation.setObjectName("dlgSelectParkingLocation")
        dlgSelectParkingLocation.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(dlgSelectParkingLocation)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listWidget = QtWidgets.QListWidget(dlgSelectParkingLocation)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(dlgSelectParkingLocation)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(dlgSelectParkingLocation)
        self.buttonBox.accepted.connect(dlgSelectParkingLocation.accept)
        self.buttonBox.rejected.connect(dlgSelectParkingLocation.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgSelectParkingLocation)

    def retranslateUi(self, dlgSelectParkingLocation):
        _translate = QtCore.QCoreApplication.translate
        dlgSelectParkingLocation.setWindowTitle(_translate("dlgSelectParkingLocation", "Select Parking Location"))
