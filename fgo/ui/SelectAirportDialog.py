# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fgo/ui/SelectAirportDialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SelectAirportDialog(object):
    def setupUi(self, SelectAirportDialog):
        SelectAirportDialog.setObjectName("SelectAirportDialog")
        SelectAirportDialog.resize(848, 538)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SelectAirportDialog.sizePolicy().hasHeightForWidth())
        SelectAirportDialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(SelectAirportDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(SelectAirportDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setObjectName("label_3")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.cbContinent = QtWidgets.QComboBox(self.tab)
        self.cbContinent.setObjectName("cbContinent")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.cbContinent)
        self.label_4 = QtWidgets.QLabel(self.tab)
        self.label_4.setObjectName("label_4")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.cbCountry = QtWidgets.QComboBox(self.tab)
        self.cbCountry.setObjectName("cbCountry")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.cbCountry)
        self.label_5 = QtWidgets.QLabel(self.tab)
        self.label_5.setObjectName("label_5")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.cbRegion = QtWidgets.QComboBox(self.tab)
        self.cbRegion.setObjectName("cbRegion")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.cbRegion)
        self.verticalLayout_3.addLayout(self.formLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout_3)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.formLayout = QtWidgets.QFormLayout(self.tab_2)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.tab_2)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(self.tab_2)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.leName = QtWidgets.QLineEdit(self.tab_2)
        self.leName.setObjectName("leName")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.leName)
        self.leAirportCode = QtWidgets.QLineEdit(self.tab_2)
        self.leAirportCode.setObjectName("leAirportCode")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.leAirportCode)
        self.pbSearch = QtWidgets.QPushButton(self.tab_2)
        self.pbSearch.setObjectName("pbSearch")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.pbSearch)
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.tableView = QtWidgets.QTableView(SelectAirportDialog)
        self.tableView.setObjectName("tableView")
        self.verticalLayout.addWidget(self.tableView)
        self.buttonBox = QtWidgets.QDialogButtonBox(SelectAirportDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SelectAirportDialog)
        self.tabWidget.setCurrentIndex(0)
        self.buttonBox.accepted.connect(SelectAirportDialog.accept)
        self.buttonBox.rejected.connect(SelectAirportDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SelectAirportDialog)

    def retranslateUi(self, SelectAirportDialog):
        _translate = QtCore.QCoreApplication.translate
        SelectAirportDialog.setWindowTitle(_translate("SelectAirportDialog", "Select Airport"))
        self.label_3.setText(_translate("SelectAirportDialog", "Continent:"))
        self.label_4.setText(_translate("SelectAirportDialog", "Country:"))
        self.label_5.setText(_translate("SelectAirportDialog", "Region:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("SelectAirportDialog", "Browse"))
        self.label.setText(_translate("SelectAirportDialog", "Airport Code:"))
        self.label_2.setText(_translate("SelectAirportDialog", "Name/Description:"))
        self.pbSearch.setText(_translate("SelectAirportDialog", "Search"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("SelectAirportDialog", "Search"))