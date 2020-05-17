# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fgo/ui/ShowErrorsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ShowErrorsDialog(object):
    def setupUi(self, ShowErrorsDialog):
        ShowErrorsDialog.setObjectName("ShowErrorsDialog")
        ShowErrorsDialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(ShowErrorsDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pteErrors = QtWidgets.QPlainTextEdit(ShowErrorsDialog)
        self.pteErrors.setReadOnly(True)
        self.pteErrors.setObjectName("pteErrors")
        self.verticalLayout.addWidget(self.pteErrors)
        self.buttonBox = QtWidgets.QDialogButtonBox(ShowErrorsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ShowErrorsDialog)
        self.buttonBox.accepted.connect(ShowErrorsDialog.accept)
        self.buttonBox.rejected.connect(ShowErrorsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ShowErrorsDialog)

    def retranslateUi(self, ShowErrorsDialog):
        _translate = QtCore.QCoreApplication.translate
        ShowErrorsDialog.setWindowTitle(_translate("ShowErrorsDialog", "Dialog"))

