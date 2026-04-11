from core.interface import PluginBase

class ImageOptimizer(PluginBase):
    @property
    def name(self) -> str:
        return "image-optimizer"

    @property
    def version(self) -> str:
        return "0.9.1"

    def activate(self) -> None:
        print("registered: post-processor for .png/.jpg")

    def deactivate(self) -> None:
        pass
