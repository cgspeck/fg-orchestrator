from PyQt5.QtWidgets import QDialog, QInputDialog, QLineEdit

from fgo.ui.CustomSettingsDialog import Ui_CustomSettingsDialog

from fgo.director.registry import CustomAgentSettings

class CustomSettingsDialog(QDialog):
    def __init__(self, settings):
        super(QDialog, self).__init__()
        self.ui = Ui_CustomSettingsDialog()
        self.ui.setupUi(self)
        self._settings = settings
        self._map_settings_to_form(settings)

        self.ui.lwAdditionalArgs.clicked.connect(self.handle_lwAdditionalArgs_clicked)
        self._selected_additional_arg = None

        self.ui.pbAddCustomArg.clicked.connect(self.handle_pbAddCustomArg_clicked)
        self.ui.pbRemoveCustomArg.clicked.connect(self.handle_pbRemoveCustomArg_clicked)
        self.ui.pbRemoveCustomArg.setEnabled(False)

    def handle_pbAddCustomArg_clicked(self, index):
        text, okPressed = QInputDialog.getText(
            self,
            'Add host',
            'Enter IP Address or hostname:',
            QLineEdit.Normal,
            ''
        )

        val = text.strip()

        if okPressed and val != "":
            self.ui.lwAdditionalArgs.addItem(val)

    def handle_pbRemoveCustomArg_clicked(self):
        if self._selected_additional_arg is not None:
            self.ui.lwAdditionalArgs.takeItem(self._selected_additional_arg)
            self.ui.pbRemoveCustomArg.setEnabled(False)
            self._selected_additional_arg = None

    def handle_lwAdditionalArgs_clicked(self, index):
        self._selected_additional_arg = index.row()
        self.ui.pbRemoveCustomArg.setEnabled(True)

    def _map_settings_to_form(self, custom_agent_settings):
        self.ui.cbDisablePanel.setChecked(custom_agent_settings.disable_panel)
        self.ui.cbDisableHUD.setChecked(custom_agent_settings.disable_hud)
        self.ui.cbDisableAntiAliasHUD.setChecked(custom_agent_settings.disable_anti_alias_hud)
        self.ui.cbEnableClouds.setChecked(custom_agent_settings.enable_clouds)
        self.ui.cbEnableClouds3D.setChecked(custom_agent_settings.enable_clouds3d)
        self.ui.cbEnableFullscreen.setChecked(custom_agent_settings.enable_fullscreen)
        self.ui.cbEnableTerraSync.setChecked(custom_agent_settings.enable_terrasync)
        self.ui.cbEnableRealWeatherFetch.setChecked(custom_agent_settings.enable_real_weather_fetch)

        if custom_agent_settings.fov is not None:
            self.ui.leFOV.setText(f"{custom_agent_settings.fov}")

        if custom_agent_settings.view_offset is not None:
            self.ui.leViewOffset.setText(f"{custom_agent_settings.view_offset}")

        for item in custom_agent_settings.additional_args:
            self.ui.lwAdditionalArgs.addItem(item)

    def _map_form_to_settings(self):
        settings = self._settings

        settings.disable_panel = self.ui.cbDisablePanel.isChecked()
        settings.disable_hud = self.ui.cbDisableHUD.isChecked()
        settings.disable_anti_alias_hud = self.ui.cbDisableAntiAliasHUD.isChecked()
        settings.enable_clouds = self.ui.cbEnableClouds.isChecked()
        settings.enable_clouds3d = self.ui.cbEnableClouds3D.isChecked()
        settings.enable_fullscreen = self.ui.cbEnableFullscreen.isChecked()
        settings.enable_terrasync = self.ui.cbEnableTerraSync.isChecked()
        settings.enable_real_weather_fetch = self.ui.cbEnableRealWeatherFetch.isChecked()

        fov_val = self.ui.leFOV.text().strip()
        if fov_val == "":
            settings.fov = None
        else:
            settings.fov = int(fov_val)

        view_offset_val = self.ui.leFOV.text().strip()
        if view_offset_val == "":
            settings.view_offset = None
        else:
            settings.view_offset = int(view_offset_val)

        settings.additional_args = []

        for item in [self.ui.lwAdditionalArgs.item(i).text() for i in range(0, self.ui.lwAdditionalArgs.count(), 1)]:
            settings.additional_args.append(item)

        return settings

    def exec_(self):
        button_res = super(CustomSettingsDialog, self).exec_()
        return self._map_form_to_settings(), button_res

    @staticmethod
    def getValues(settings: CustomAgentSettings):
        dialog = CustomSettingsDialog(settings)
        return dialog.exec_()
