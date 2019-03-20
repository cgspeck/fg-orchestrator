import typing
from dataclasses import dataclass, field

@dataclass
class CustomAgentSettings:
    # visible
    additional_args: typing.List[str] = field(default_factory=list)
    disable_panel: bool = False
    disable_hud: bool = False
    disable_anti_alias_hud: bool = False
    enable_clouds: bool = False
    enable_clouds3d: bool = False
    enable_fullscreen: bool = True
    enable_terrasync: bool = True
    enable_real_weather_fetch: bool = True
    fov: typing.Union[int, None] = None
    view_offset: typing.Union[int, None] = 0
    # hidden
    role: int = None  # 0 or 1
    master_ip_address: str = None
    client_ip_addresses: typing.List[str] = field(default_factory=list)

    def to_update_dict(self) -> typing.Dict[str, typing.Union[str, list, None]]:
        '''Distill only the properties we want to update into a dict for the config dialog'''
        memo = {}
        memo['additional_args'] = self.additional_args
        memo['disable_panel'] = self.disable_panel
        memo['disable_hud'] = self.disable_hud
        memo['disable_anti_alias_hud'] = self.disable_anti_alias_hud
        memo['enable_clouds'] = self.enable_clouds
        memo['enable_clouds3d'] = self.enable_clouds3d
        memo['enable_fullscreen'] = self.enable_fullscreen
        memo['enable_terrasync'] = self.enable_terrasync
        memo['enable_real_weather_fetch'] = self.enable_real_weather_fetch
        memo['fov'] = self.fov
        memo['view_offset'] = self.view_offset
        return memo

    def apply_update_dict(self, update_dictionary: typing.Dict[str, typing.Union[str, list, None]]):
        '''Merge current values with an update message from the config dialog'''
        logging.info(f"CustomAgentSettings applying update dict: {update_dictionary}")
        self.additional_args = update_dictionary['additional_args']
        self.disable_panel = update_dictionary['disable_panel']
        self.disable_hud = update_dictionary['disable_hud']
        self.disable_anti_alias_hud = update_dictionary['disable_anti_alias_hud']
        self.enable_clouds = update_dictionary['enable_clouds']
        self.enable_clouds3d = update_dictionary['enable_clouds3d']
        self.enable_fullscreen = update_dictionary['enable_fullscreen']
        self.enable_terrasync = update_dictionary['enable_terrasync']
        self.enable_real_weather_fetch = update_dictionary['enable_real_weather_fetch']
        self.fov = update_dictionary['fov']
        self.view_offset = update_dictionary['view_offset']

        return self
