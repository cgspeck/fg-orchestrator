import logging
import typing
from dataclasses import dataclass, field

@dataclass
class CustomAgentSettings:
    # visible
    additional_args: typing.List[str] = field(default_factory=list)
    disable_ai: bool = False
    disable_ai_traffic: bool = False
    disable_anti_alias_hud: bool = False
    disable_hud: bool = False
    disable_panel: bool = False
    disable_sound: bool = False
    enable_clouds: bool = False
    enable_clouds3d: bool = False
    enable_fullscreen: bool = True
    enable_terrasync: bool = True
    enable_telnet_server: bool = False
    enable_real_weather_fetch: bool = True
    enable_web_server: bool = False
    fov: typing.Union[float, None] = None
    view_offset: typing.Union[int, None] = 0
    # hidden
    role: int = None  # 0 or 1
    master_ip_address: str = None
    client_ip_addresses: typing.List[str] = field(default_factory=list)

    def to_update_dict(self) -> typing.Dict[str, typing.Union[str, list, None]]:
        '''Distill only the properties we want to update into a dict for the config dialog'''
        memo = {}
        memo['additional_args'] = self.additional_args
        memo['disable_ai'] = self.disable_ai
        memo['disable_ai_traffic'] = self.disable_ai_traffic
        memo['disable_anti_alias_hud'] = self.disable_anti_alias_hud
        memo['disable_hud'] = self.disable_hud
        memo['disable_panel'] = self.disable_panel
        memo['disable_sound'] = self.disable_sound
        memo['enable_clouds'] = self.enable_clouds
        memo['enable_clouds3d'] = self.enable_clouds3d
        memo['enable_fullscreen'] = self.enable_fullscreen
        memo['enable_terrasync'] = self.enable_terrasync
        memo['enable_telnet_server'] = self.enable_telnet_server
        memo['enable_real_weather_fetch'] = self.enable_real_weather_fetch
        memo['enable_web_server'] = self.enable_web_server
        memo['fov'] = self.fov
        memo['view_offset'] = self.view_offset
        return memo

    def apply_update_dict(self, update_dictionary: typing.Dict[str, typing.Union[str, list, None]]):
        '''Merge current values with an update message from the config dialog'''
        logging.info(f"CustomAgentSettings applying update dict: {update_dictionary}")
        self.additional_args = update_dictionary.get('additional_args', [])
        self.disable_ai = update_dictionary.get('disable_ai', False)
        self.disable_ai_traffic = update_dictionary.get('disable_ai_traffic', False)
        self.disable_anti_alias_hud = update_dictionary.get('disable_anti_alias_hud', False)
        self.disable_hud = update_dictionary.get('disable_hud', False)
        self.disable_panel = update_dictionary.get('disable_panel', False)
        self.disable_sound = update_dictionary.get('disable_sound', False)
        self.enable_clouds = update_dictionary.get('enable_clouds', False)
        self.enable_clouds3d = update_dictionary.get('enable_clouds3d', False)
        self.enable_fullscreen = update_dictionary.get('enable_fullscreen', True)
        self.enable_terrasync = update_dictionary.get('enable_terrasync', True)
        self.enable_telnet_server = update_dictionary.get('enable_telnet_server', False)
        self.enable_real_weather_fetch = update_dictionary.get('enable_real_weather_fetch', True)
        self.enable_web_server = update_dictionary.get('enable_web_server', True)
        self.fov = update_dictionary.get('fov', None)
        self.view_offset = update_dictionary.get('view_offset', 0)

        return self
