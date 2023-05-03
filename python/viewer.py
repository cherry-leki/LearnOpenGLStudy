
from abc import abstractmethod


class GLContent:
    def __init__(self, window, viewport, camera, file_path):
        self.window    = window
        self.viewport  = viewport
        self.camera    = camera
        self.file_path = file_path

    @abstractmethod
    def inspector(self):
        pass

    @abstractmethod
    def render(self, *args):
        pass

    @abstractmethod
    def destroy(self):
        pass
