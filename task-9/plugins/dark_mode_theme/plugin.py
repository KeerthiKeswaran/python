from core.interface import PluginBase

class DarkModeTheme(PluginBase):
    @property
    def name(self) -> str:
        return "dark-mode-theme"

    @property
    def version(self) -> str:
        return "1.3.2"

    def activate(self) -> None:
        print("registered: theme \"dark-mode\"")

    def deactivate(self) -> None:
        pass
