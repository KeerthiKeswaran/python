from core.interface import PluginBase

class MarkdownParser(PluginBase):
    @property
    def name(self) -> str:
        return "markdown-parser"

    @property
    def version(self) -> str:
        return "2.1.0"

    def activate(self) -> None:
        print("registered: .md -> HTML converter")

    def deactivate(self) -> None:
        pass
