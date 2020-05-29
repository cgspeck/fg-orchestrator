# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fgo/ui/MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(828, 882)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/common/assets/fgo_32x32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setIconSize(QtCore.QSize(32, 32))
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
        self.leAircraft = QtWidgets.QLineEdit(self.frame_2)
        self.leAircraft.setObjectName("leAircraft")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.leAircraft)
        self.label_9 = QtWidgets.QLabel(self.frame_2)
        self.label_9.setObjectName("label_9")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_9)
        self.leAircraftVariant = QtWidgets.QLineEdit(self.frame_2)
        self.leAircraftVariant.setObjectName("leAircraftVariant")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.leAircraftVariant)
        self.leAircraftLink = QtWidgets.QLabel(self.frame_2)
        self.leAircraftLink.setOpenExternalLinks(True)
        self.leAircraftLink.setObjectName("leAircraftLink")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.leAircraftLink)
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.cbTimeOfDay = QtWidgets.QComboBox(self.frame_2)
        self.cbTimeOfDay.setObjectName("cbTimeOfDay")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.cbTimeOfDay)
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.cbMasterAgent = QtWidgets.QComboBox(self.frame_2)
        self.cbMasterAgent.setObjectName("cbMasterAgent")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.cbMasterAgent)
        self.labelPhiLink = QtWidgets.QLabel(self.frame_2)
        self.labelPhiLink.setText("")
        self.labelPhiLink.setOpenExternalLinks(True)
        self.labelPhiLink.setObjectName("labelPhiLink")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.labelPhiLink)
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
        self.rbAirport = QtWidgets.QRadioButton(self.frame_5)
        self.rbAirport.setChecked(False)
        self.rbAirport.setObjectName("rbAirport")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.rbAirport)
        self.rbCarrier = QtWidgets.QRadioButton(self.frame_5)
        self.rbCarrier.setObjectName("rbCarrier")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.rbCarrier)
        self.leCarrier = QtWidgets.QLineEdit(self.frame_5)
        self.leCarrier.setObjectName("leCarrier")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.leCarrier)
        self.leAirport = QtWidgets.QLabel(self.frame_5)
        font = QtGui.QFont()
        font.setUnderline(False)
        self.leAirport.setFont(font)
        self.leAirport.setObjectName("leAirport")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.leAirport)
        self.pbSelectAirport = QtWidgets.QPushButton(self.frame_5)
        self.pbSelectAirport.setObjectName("pbSelectAirport")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.pbSelectAirport)
        self.rbDefaultAirport = QtWidgets.QRadioButton(self.frame_5)
        self.rbDefaultAirport.setChecked(True)
        self.rbDefaultAirport.setObjectName("rbDefaultAirport")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.rbDefaultAirport)
        self.horizontalLayout_4.addWidget(self.frame_5)
        self.frame_4 = QtWidgets.QFrame(self.frame_3)
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.formLayout_3 = QtWidgets.QFormLayout(self.frame_4)
        self.formLayout_3.setObjectName("formLayout_3")
        self.rbRunway = QtWidgets.QRadioButton(self.frame_4)
        self.rbRunway.setChecked(False)
        self.rbRunway.setObjectName("rbRunway")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.rbRunway)
        self.rbParking = QtWidgets.QRadioButton(self.frame_4)
        self.rbParking.setObjectName("rbParking")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.rbParking)
        self.leRunway = QtWidgets.QLineEdit(self.frame_4)
        self.leRunway.setObjectName("leRunway")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.leRunway)
        self.leParking = QtWidgets.QLineEdit(self.frame_4)
        self.leParking.setObjectName("leParking")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.leParking)
        self.rbDefaultRunway = QtWidgets.QRadioButton(self.frame_4)
        self.rbDefaultRunway.setChecked(True)
        self.rbDefaultRunway.setObjectName("rbDefaultRunway")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.rbDefaultRunway)
        self.pbSelectParking = QtWidgets.QPushButton(self.frame_4)
        self.pbSelectParking.setObjectName("pbSelectParking")
        self.formLayout_3.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.pbSelectParking)
        self.horizontalLayout_4.addWidget(self.frame_4)
        self.verticalLayout_2.addWidget(self.frame_3)
        self.tabScenarioSettings.addTab(self.groupScenarioSettingsPage1_2, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame_6 = QtWidgets.QFrame(self.tab)
        self.frame_6.setMinimumSize(QtCore.QSize(30, 30))
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.formLayout_5 = QtWidgets.QFormLayout(self.frame_6)
        self.formLayout_5.setObjectName("formLayout_5")
        self.label = QtWidgets.QLabel(self.frame_6)
        self.label.setObjectName("label")
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.leTSEndpoint = QtWidgets.QLineEdit(self.frame_6)
        self.leTSEndpoint.setObjectName("leTSEndpoint")
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.leTSEndpoint)
        self.label_5 = QtWidgets.QLabel(self.frame_6)
        self.label_5.setObjectName("label_5")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.leCeiling = QtWidgets.QLineEdit(self.frame_6)
        self.leCeiling.setObjectName("leCeiling")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.leCeiling)
        self.label_4 = QtWidgets.QLabel(self.frame_6)
        self.label_4.setObjectName("label_4")
        self.formLayout_5.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.cbAutoCoordination = QtWidgets.QCheckBox(self.frame_6)
        self.cbAutoCoordination.setText("")
        self.cbAutoCoordination.setChecked(True)
        self.cbAutoCoordination.setObjectName("cbAutoCoordination")
        self.formLayout_5.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.cbAutoCoordination)
        self.label_7 = QtWidgets.QLabel(self.frame_6)
        self.label_7.setObjectName("label_7")
        self.formLayout_5.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.leVisibilityMeters = QtWidgets.QLineEdit(self.frame_6)
        self.leVisibilityMeters.setObjectName("leVisibilityMeters")
        self.formLayout_5.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.leVisibilityMeters)
        self.pbManageAIScenarios = QtWidgets.QPushButton(self.frame_6)
        self.pbManageAIScenarios.setEnabled(False)
        self.pbManageAIScenarios.setCheckable(False)
        self.pbManageAIScenarios.setObjectName("pbManageAIScenarios")
        self.formLayout_5.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.pbManageAIScenarios)
        self.label_8 = QtWidgets.QLabel(self.frame_6)
        self.label_8.setText("")
        self.label_8.setObjectName("label_8")
        self.formLayout_5.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_8)
        self.cbSkipAircraftInstall = QtWidgets.QCheckBox(self.frame_6)
        self.cbSkipAircraftInstall.setText("")
        self.cbSkipAircraftInstall.setObjectName("cbSkipAircraftInstall")
        self.formLayout_5.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.cbSkipAircraftInstall)
        self.label_10 = QtWidgets.QLabel(self.frame_6)
        self.label_10.setObjectName("label_10")
        self.formLayout_5.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_10)
        self.verticalLayout_3.addWidget(self.frame_6)
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
        self.pbLaunch = QtWidgets.QPushButton(self.groupControls)
        self.pbLaunch.setEnabled(False)
        self.pbLaunch.setObjectName("pbLaunch")
        self.horizontalLayout.addWidget(self.pbLaunch)
        self.pbStop = QtWidgets.QPushButton(self.groupControls)
        self.pbStop.setEnabled(False)
        self.pbStop.setObjectName("pbStop")
        self.horizontalLayout.addWidget(self.pbStop)
        self.verticalLayout.addWidget(self.groupControls)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.tvAgents = QtWidgets.QTableView(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tvAgents.sizePolicy().hasHeightForWidth())
        self.tvAgents.setSizePolicy(sizePolicy)
        self.tvAgents.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tvAgents.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tvAgents.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tvAgents.setObjectName("tvAgents")
        self.gridLayout.addWidget(self.tvAgents, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 828, 22))
        self.menubar.setObjectName("menubar")
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.action_Log = QtWidgets.QAction(MainWindow)
        self.action_Log.setObjectName("action_Log")
        self.actionAddHost = QtWidgets.QAction(MainWindow)
        self.actionAddHost.setObjectName("actionAddHost")
        self.actionLoad_Secnario = QtWidgets.QAction(MainWindow)
        self.actionLoad_Secnario.setEnabled(True)
        self.actionLoad_Secnario.setVisible(True)
        self.actionLoad_Secnario.setObjectName("actionLoad_Secnario")
        self.actionSave_Scenario = QtWidgets.QAction(MainWindow)
        self.actionSave_Scenario.setEnabled(True)
        self.actionSave_Scenario.setObjectName("actionSave_Scenario")
        self.actionNew_Scenario = QtWidgets.QAction(MainWindow)
        self.actionNew_Scenario.setEnabled(True)
        self.actionNew_Scenario.setVisible(True)
        self.actionNew_Scenario.setObjectName("actionNew_Scenario")
        self.actionSave_As = QtWidgets.QAction(MainWindow)
        self.actionSave_As.setEnabled(False)
        self.actionSave_As.setObjectName("actionSave_As")
        self.menu_File.addAction(self.actionNew_Scenario)
        self.menu_File.addAction(self.actionLoad_Secnario)
        self.menu_File.addAction(self.actionSave_Scenario)
        self.menu_File.addAction(self.actionSave_As)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionAddHost)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionExit)
        self.menubar.addAction(self.menu_File.menuAction())

        self.retranslateUi(MainWindow)
        self.tabScenarioSettings.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.pbLaunch, self.pbStop)
        MainWindow.setTabOrder(self.pbStop, self.tabScenarioSettings)
        MainWindow.setTabOrder(self.tabScenarioSettings, self.leAircraft)
        MainWindow.setTabOrder(self.leAircraft, self.tvAgents)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "FlightGear Orchestrator"))
        self.label_6.setText(_translate("MainWindow", "Aircraft:"))
        self.leAircraft.setText(_translate("MainWindow", "c172p"))
        self.label_9.setText(_translate("MainWindow", "Variant:"))
        self.leAircraftVariant.setText(_translate("MainWindow", "c172p"))
        self.leAircraftLink.setText(_translate("MainWindow", "<a href=\"https://svn.code.sf.net/p/flightgear/fgaddon/trunk/Aircraft/\">View latest release aircraft</a>"))
        self.label_2.setText(_translate("MainWindow", "Time of Day:"))
        self.label_3.setText(_translate("MainWindow", "Master:"))
        self.cbMasterAgent.setToolTip(_translate("MainWindow", "Select an agent to be master, must be online and ready"))
        self.rbAirport.setText(_translate("MainWindow", "Airport:"))
        self.rbCarrier.setText(_translate("MainWindow", "Carrier:"))
        self.leAirport.setText(_translate("MainWindow", "YMML"))
        self.pbSelectAirport.setText(_translate("MainWindow", "Select Airport && Runway..."))
        self.rbDefaultAirport.setText(_translate("MainWindow", "Deafult Airport"))
        self.rbRunway.setText(_translate("MainWindow", "Runway:"))
        self.rbParking.setText(_translate("MainWindow", "Parking:"))
        self.leRunway.setText(_translate("MainWindow", "09"))
        self.rbDefaultRunway.setText(_translate("MainWindow", "Default Runway"))
        self.pbSelectParking.setText(_translate("MainWindow", "Select Parking..."))
        self.tabScenarioSettings.setTabText(self.tabScenarioSettings.indexOf(self.groupScenarioSettingsPage1_2), _translate("MainWindow", "Basic Scenario Settings"))
        self.label.setText(_translate("MainWindow", "Terrasync Endpoint:"))
        self.leTSEndpoint.setText(_translate("MainWindow", "http://flightgear.sourceforge.net/scenery"))
        self.label_5.setText(_translate("MainWindow", "Ceiling HEIGHT[:THICKNESS]"))
        self.label_4.setText(_translate("MainWindow", "Enable auto-coordination:"))
        self.label_7.setText(_translate("MainWindow", "Visibility in meters:"))
        self.pbManageAIScenarios.setText(_translate("MainWindow", "Manage AI Scenarios"))
        self.label_10.setText(_translate("MainWindow", "Skip Aircraft Installation Phase:"))
        self.tabScenarioSettings.setTabText(self.tabScenarioSettings.indexOf(self.tab), _translate("MainWindow", "Advanced Scenario Settings"))
        self.groupControls.setTitle(_translate("MainWindow", "Controls"))
        self.pbLaunch.setText(_translate("MainWindow", "Launch"))
        self.pbStop.setText(_translate("MainWindow", "Stop"))
        self.groupBox.setTitle(_translate("MainWindow", "Agents"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.actionExit.setText(_translate("MainWindow", "E&xit"))
        self.action_Log.setText(_translate("MainWindow", "&Log"))
        self.actionAddHost.setText(_translate("MainWindow", "Add &Host..."))
        self.actionLoad_Secnario.setText(_translate("MainWindow", "Open..."))
        self.actionSave_Scenario.setText(_translate("MainWindow", "Save"))
        self.actionNew_Scenario.setText(_translate("MainWindow", "New"))
        self.actionSave_As.setText(_translate("MainWindow", "Save As..."))
from . import resources_rc
