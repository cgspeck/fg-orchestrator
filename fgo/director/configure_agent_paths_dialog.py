import typing

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSlot

from fgo.ui.ConfigureAgentPaths import Ui_ConfigureAgentPathsDialog

from fgo.director.agent_directory_settings import AgentDirectorySettings
from fgo.director.registry import Registry

from fgo.director.select_remote_path_dialog import SelectRemotePathDialog

class ConfigureAgentPathsDialog(QDialog):
    def __init__(self, agent_directory_settings, registry, hostname):
        super(QDialog, self).__init__()
        self.ui = Ui_ConfigureAgentPathsDialog()
        self.ui.setupUi(self)

        self._registry = registry
        self._hostname = hostname
        self._map_settings_to_form(agent_directory_settings)

    def _map_settings_to_form(self, agent_directory_settings):
        if agent_directory_settings.flightgear_executable is not None:
            self.ui.leFgfsExec.setText(agent_directory_settings.flightgear_executable)

        if agent_directory_settings.fgroot_path is not None:
            self.ui.leFGRoot.setText(agent_directory_settings.fgroot_path)

        if agent_directory_settings.fghome_path is not None:
            self.ui.leFGHome.setText(agent_directory_settings.fghome_path)

        if agent_directory_settings.terrasync_path is not None:
            self.ui.leTSPath.setText(agent_directory_settings.terrasync_path)

        if agent_directory_settings.aircraft_path is not None:
            self.ui.leAircraft.setText(agent_directory_settings.aircraft_path)

    @pyqtSlot()
    def on_pbFGExec_clicked(self):
        ok, res = self.show_remote_chooser(
            self.ui.leFgfsExec.text()
        )

        if ok:
            self.ui.leFgfsExec.setText(res)

    @pyqtSlot()
    def on_pbFGRoot_clicked(self):
        ok, res = self.show_remote_chooser(
            self.ui.leFGRoot.text(),
            select_file=False
        )

        if ok:
            self.ui.leFGRoot.setText(res)

    @pyqtSlot()
    def on_pbFGHome_clicked(self):
        ok, res = self.show_remote_chooser(
            self.ui.leFGHome.text(),
            select_file=False
        )

        if ok:
            self.ui.leFGHome.setText(res)

    @pyqtSlot()
    def on_pbTS_clicked(self):
        ok, res = self.show_remote_chooser(
            self.ui.leTSPath.text(),
            select_file=False,
            allow_none=True
        )

        if ok:
            self.ui.leTSPath.setText(res)

    @pyqtSlot()
    def on_pbAircraft_clicked(self):
        ok, res = self.show_remote_chooser(
            self.ui.leAircraft.text(),
            select_file=False,
            allow_none=True
        )

        if ok:
            self.ui.leAircraft.setText(res)

    def show_remote_chooser(self, current_selection=str, select_file=True, allow_none=False) -> typing.Tuple[typing.Union[str, None], bool]:
        """
        Shows a remote file/folder chooser

        Returns:
            str or None
            ok (! cancel pressed)

        """
        return SelectRemotePathDialog.getValue(
            current_selection,
            self._hostname,
            self._registry,
            select_file,
            allow_none
        )

    def _map_form_to_settings(self):
        # settings = self._settings
        #
        # settings.disable_panel = self.ui.cbDisablePanel.isChecked()
        # settings.disable_hud = self.ui.cbDisableHUD.isChecked()
        # settings.disable_anti_alias_hud = self.ui.cbDisableAntiAliasHUD.isChecked()
        # settings.enable_clouds = self.ui.cbEnableClouds.isChecked()
        # settings.enable_clouds3d = self.ui.cbEnableClouds3D.isChecked()
        # settings.enable_fullscreen = self.ui.cbEnableFullscreen.isChecked()
        # settings.enable_terrasync = self.ui.cbEnableTerraSync.isChecked()
        # settings.enable_real_weather_fetch = self.ui.cbEnableRealWeatherFetch.isChecked()
        #
        # fov_val = self.ui.leFOV.text().strip()
        # if fov_val == "":
        #     settings.fov = None
        # else:
        #     settings.fov = int(fov_val)
        #
        # view_offset_val = self.ui.leFOV.text().strip()
        # if view_offset_val == "":
        #     settings.view_offset = None
        # else:
        #     settings.view_offset = int(view_offset_val)
        #
        # settings.additional_args = []
        #
        # for item in [self.ui.lwAdditionalArgs.item(i).text() for i in range(0, self.ui.lwAdditionalArgs.count(), 1)]:
        #     settings.additional_args.append(item)
        return None

    def exec_(self):
        button_res = super(ConfigureAgentPathsDialog, self).exec_()
        return self._map_form_to_settings(), button_res

    @staticmethod
    def getValues(settings: AgentDirectorySettings, registry: Registry, hostname: str):
        dialog = ConfigureAgentPathsDialog(settings, registry, hostname)
        return dialog.exec_()
