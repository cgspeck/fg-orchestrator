# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fgo/ui/MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(814, 671)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabScenarioSettings = QtWidgets.QTabWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabScenarioSettings.sizePolicy().hasHeightForWidth())
        self.tabScenarioSettings.setSizePolicy(sizePolicy)
        self.tabScenarioSettings.setObjectName("tabScenarioSettings")
        self.groupScenarioSettingsPage1_2 = QtWidgets.QWidget()
        self.groupScenarioSettingsPage1_2.setObjectName("groupScenarioSettingsPage1_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupScenarioSettingsPage1_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame_2 = QtWidgets.QFrame(self.groupScenarioSettingsPage1_2)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.formLayout = QtWidgets.QFormLayout(self.frame_2)
        self.formLayout.setObjectName("formLayout")
        self.label_6 = QtWidgets.QLabel(self.frame_2)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.lineEdit_6 = QtWidgets.QLineEdit(self.frame_2)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_6)
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.comboBox = QtWidgets.QComboBox(self.frame_2)
        self.comboBox.setObjectName("comboBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.comboBox)
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.comboBox_2 = QtWidgets.QComboBox(self.frame_2)
        self.comboBox_2.setObjectName("comboBox_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.comboBox_2)
        self.verticalLayout_2.addWidget(self.frame_2)
        self.frame_3 = QtWidgets.QFrame(self.groupScenarioSettingsPage1_2)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.frame_5 = QtWidgets.QFrame(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_5.sizePolicy().hasHeightForWidth())
        self.frame_5.setSizePolicy(sizePolicy)
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.formLayout_2 = QtWidgets.QFormLayout(self.frame_5)
        self.formLayout_2.setObjectName("formLayout_2")
        self.radioButton_2 = QtWidgets.QRadioButton(self.frame_5)
        self.radioButton_2.setChecked(True)
        self.radioButton_2.setObjectName("radioButton_2")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.radioButton_2)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.frame_5)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_2)
        self.radioButton = QtWidgets.QRadioButton(self.frame_5)
        self.radioButton.setObjectName("radioButton")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.radioButton)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.frame_5)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_3)
        self.horizontalLayout_4.addWidget(self.frame_5)
        self.frame_4 = QtWidgets.QFrame(self.frame_3)
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.formLayout_3 = QtWidgets.QFormLayout(self.frame_4)
        self.formLayout_3.setObjectName("formLayout_3")
        self.radioButton_3 = QtWidgets.QRadioButton(self.frame_4)
        self.radioButton_3.setChecked(True)
        self.radioButton_3.setObjectName("radioButton_3")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.radioButton_3)
        self.radioButton_4 = QtWidgets.QRadioButton(self.frame_4)
        self.radioButton_4.setObjectName("radioButton_4")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.radioButton_4)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.frame_4)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_4)
        self.lineEdit_7 = QtWidgets.QLineEdit(self.frame_4)
        self.lineEdit_7.setObjectName("lineEdit_7")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_7)
        self.horizontalLayout_4.addWidget(self.frame_4)
        self.verticalLayout_2.addWidget(self.frame_3)
        self.tabScenarioSettings.addTab(self.groupScenarioSettingsPage1_2, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.formLayout_4 = QtWidgets.QFormLayout(self.tab)
        self.formLayout_4.setObjectName("formLayout_4")
        self.label_5 = QtWidgets.QLabel(self.tab)
        self.label_5.setObjectName("label_5")
        self.formLayout_4.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.lineEdit_5 = QtWidgets.QLineEdit(self.tab)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.formLayout_4.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.lineEdit_5)
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.frame = QtWidgets.QFrame(self.groupBox_2)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setEnabled(False)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.gridLayout_2.addWidget(self.frame, 1, 0, 1, 1)
        self.listWidget = QtWidgets.QListWidget(self.groupBox_2)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout_2.addWidget(self.listWidget, 0, 0, 1, 1)
        self.formLayout_4.setWidget(5, QtWidgets.QFormLayout.SpanningRole, self.groupBox_2)
        self.lineEdit = QtWidgets.QLineEdit(self.tab)
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout_4.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setObjectName("label")
        self.formLayout_4.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label)
        self.lineEdit_5.raise_()
        self.groupBox_2.raise_()
        self.label_5.raise_()
        self.lineEdit.raise_()
        self.label.raise_()
        self.tabScenarioSettings.addTab(self.tab, "")
        self.verticalLayout.addWidget(self.tabScenarioSettings)
        self.groupControls = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupControls.sizePolicy().hasHeightForWidth())
        self.groupControls.setSizePolicy(sizePolicy)
        self.groupControls.setObjectName("groupControls")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupControls)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnLaunch = QtWidgets.QPushButton(self.groupControls)
        self.btnLaunch.setEnabled(False)
        self.btnLaunch.setObjectName("btnLaunch")
        self.horizontalLayout.addWidget(self.btnLaunch)
        self.btnStop = QtWidgets.QPushButton(self.groupControls)
        self.btnStop.setEnabled(False)
        self.btnStop.setObjectName("btnStop")
        self.horizontalLayout.addWidget(self.btnStop)
        self.verticalLayout.addWidget(self.groupControls)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.tableWidget = QtWidgets.QTableWidget(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 814, 22))
        self.menubar.setObjectName("menubar")
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        self.menu_View = QtWidgets.QMenu(self.menubar)
        self.menu_View.setObjectName("menu_View")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionE_xit = QtWidgets.QAction(MainWindow)
        self.actionE_xit.setObjectName("actionE_xit")
        self.action_Log = QtWidgets.QAction(MainWindow)
        self.action_Log.setObjectName("action_Log")
        self.menu_File.addAction(self.actionE_xit)
        self.menu_View.addAction(self.action_Log)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_View.menuAction())

        self.retranslateUi(MainWindow)
        self.tabScenarioSettings.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.btnLaunch, self.btnStop)
        MainWindow.setTabOrder(self.btnStop, self.tabScenarioSettings)
        MainWindow.setTabOrder(self.tabScenarioSettings, self.lineEdit_6)
        MainWindow.setTabOrder(self.lineEdit_6, self.tableWidget)
        MainWindow.setTabOrder(self.tableWidget, self.lineEdit)
        MainWindow.setTabOrder(self.lineEdit, self.lineEdit_5)
        MainWindow.setTabOrder(self.lineEdit_5, self.listWidget)
        MainWindow.setTabOrder(self.listWidget, self.pushButton_2)
        MainWindow.setTabOrder(self.pushButton_2, self.pushButton)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "FlightGear Orchestrator"))
        self.label_6.setText(_translate("MainWindow", "Aircraft:"))
        self.lineEdit_6.setText(_translate("MainWindow", "c172p"))
        self.label_2.setText(_translate("MainWindow", "Time of Day:"))
        self.label_3.setText(_translate("MainWindow", "Master:"))
        self.radioButton_2.setText(_translate("MainWindow", "Airport:"))
        self.lineEdit_2.setText(_translate("MainWindow", "YBBN"))
        self.radioButton.setText(_translate("MainWindow", "Carrier:"))
        self.radioButton_3.setText(_translate("MainWindow", "Runway:"))
        self.radioButton_4.setText(_translate("MainWindow", "Parking:"))
        self.lineEdit_4.setText(_translate("MainWindow", "01"))
        self.tabScenarioSettings.setTabText(self.tabScenarioSettings.indexOf(self.groupScenarioSettingsPage1_2), _translate("MainWindow", "Basic Scenario Settings"))
        self.label_5.setText(_translate("MainWindow", "Ceiling HEIGHT[:THICKNESS]"))
        self.groupBox_2.setTitle(_translate("MainWindow", "AI Scenarios"))
        self.pushButton_2.setText(_translate("MainWindow", "Add"))
        self.pushButton.setText(_translate("MainWindow", "Remove"))
        self.lineEdit.setText(_translate("MainWindow", "http://flightgear.sourceforge.net/scenery"))
        self.label.setText(_translate("MainWindow", "Terrasync Endpoint:"))
        self.tabScenarioSettings.setTabText(self.tabScenarioSettings.indexOf(self.tab), _translate("MainWindow", "Advanced Scenario Settings"))
        self.groupControls.setTitle(_translate("MainWindow", "Controls"))
        self.btnLaunch.setText(_translate("MainWindow", "Launch"))
        self.btnStop.setText(_translate("MainWindow", "Stop"))
        self.groupBox.setTitle(_translate("MainWindow", "Agents"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.menu_View.setTitle(_translate("MainWindow", "&View"))
        self.actionE_xit.setText(_translate("MainWindow", "E&xit"))
        self.action_Log.setText(_translate("MainWindow", "&Log"))

