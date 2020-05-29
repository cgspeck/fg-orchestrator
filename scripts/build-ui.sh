#! /bin/bash -e
./venv/bin/pyuic5 --from-imports fgo/ui/MainWindow.ui -o fgo/ui/MainWindow.py
./venv/bin/pyuic5 fgo/ui/CustomSettingsDialog.ui -o fgo/ui/CustomSettingsDialog.py
./venv/bin/pyuic5 fgo/ui/AiScenariosDialog.ui -o fgo/ui/AiScenariosDialog.py
./venv/bin/pyuic5  --from-imports fgo/ui/ConfigureAgentPaths.ui -o fgo/ui/ConfigureAgentPaths.py
./venv/bin/pyuic5 fgo/ui/SelectRemotePathDialog.ui -o fgo/ui/SelectRemotePathDialog.py
./venv/bin/pyuic5 fgo/ui/ShowErrorsDialog.ui -o fgo/ui/ShowErrorsDialog.py
./venv/bin/pyuic5 fgo/ui/SelectAirportDialog.ui -o fgo/ui/SelectAirportDialog.py
./venv/bin/pyuic5 fgo/ui/SelectParkingLocationDialog.ui -o fgo/ui/SelectParkingLocationDialog.py
./venv/bin/pyrcc5 fgo/ui/resources.qrc -o fgo/ui/resources_rc.py
