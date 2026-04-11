from core.interface import PluginBase
from typing import List

class RSSFeed(PluginBase):
    @property
    def name(self) -> str:
        return "rss-feed"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def dependencies(self) -> List[str]:
        return ["markdown-parser"]

    def activate(self) -> None:
        print("registered: command \"generate-rss\"")

    def deactivate(self) -> None:
        pass
