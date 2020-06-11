from dataclasses import dataclass, field


@dataclass
class WebPanelRecord:
    name: str = None
    file_name: str = None

    def generate_url(self, host_address: str) -> str:
        return f'http://{host_address}:8080/aircraft-dir/WebPanel/{self.file_name}'

    def generate_link_tag(self, host_address: str) -> str:
        return f'<a href="{self.generate_url(host_address)}">{self.name}</a>'
