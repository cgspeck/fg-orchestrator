#! /bin/bash -e
pyuic5 fgo/ui/MainWindow.ui -o fgo/ui/MainWindow.py
pyuic5 fgo/ui/CustomSettingsDialog.ui -o fgo/ui/CustomSettingsDialog.py
pyuic5 fgo/ui/AiScenariosDialog.ui -o fgo/ui/AiScenariosDialog.py
pyuic5 fgo/ui/ConfigureAgentPaths.ui -o fgo/ui/ConfigureAgentPaths.py 
