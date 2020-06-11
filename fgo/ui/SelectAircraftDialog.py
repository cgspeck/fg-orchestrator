# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fgo/ui/SelectAircraftDialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SelectAircraftDialog(object):
    def setupUi(self, SelectAircraftDialog):
        SelectAircraftDialog.setObjectName("SelectAircraftDialog")
        SelectAircraftDialog.resize(805, 517)
        self.verticalLayout = QtWidgets.QVBoxLayout(SelectAircraftDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(SelectAircraftDialog)
        self.frame.setMaximumSize(QtCore.QSize(16777215, 105))
        self.frame.setObjectName("frame")
        self.formLayout = QtWidgets.QFormLayout(self.frame)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.cbStatus = QtWidgets.QComboBox(self.frame)
        self.cbStatus.setObjectName("cbStatus")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.cbStatus)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.leNameDescription = QtWidgets.QLineEdit(self.frame)
        self.leNameDescription.setObjectName("leNameDescription")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.leNameDescription)
        self.pbSearch = QtWidgets.QPushButton(self.frame)
        self.pbSearch.setObjectName("pbSearch")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.pbSearch)
        self.verticalLayout.addWidget(self.frame)
        self.tableView = QtWidgets.QTableView(SelectAircraftDialog)
        self.tableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setObjectName("tableView")
        self.verticalLayout.addWidget(self.tableView)
        self.buttonBox = QtWidgets.QDialogButtonBox(SelectAircraftDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SelectAircraftDialog)
        self.buttonBox.accepted.connect(SelectAircraftDialog.accept)
        self.buttonBox.rejected.connect(SelectAircraftDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SelectAircraftDialog)

    def retranslateUi(self, SelectAircraftDialog):
        _translate = QtCore.QCoreApplication.translate
        SelectAircraftDialog.setWindowTitle(_translate("SelectAircraftDialog", "Select Aircraft"))
        self.label.setText(_translate("SelectAircraftDialog", "Status >=: "))
        self.label_2.setText(_translate("SelectAircraftDialog", "Name/Description:"))
        self.pbSearch.setText(_translate("SelectAircraftDialog", "Search"))
