from collections.abc import Callable

from PyQt5.QtCore import *

from Compressor import Compressor
from Models import ImageFile


class CompressWorker(QObject):
    image_file_signal = pyqtSignal(ImageFile)
    err_signal = pyqtSignal(BaseException)
    finished = pyqtSignal(int)  # if int != 0: Interrupted

    def __init__(self):
        super().__init__()
        self.compressor = Compressor()
        self.avg_quality = 0
        self.image_files = list()

    def run(self):
        self.compressor.compress(
            avg_quality=self.avg_quality,
            image_files=self.image_files,
            image_file_signal=self.image_file_signal,
            err_signal=self.err_signal
        )
        QThread.sleep(1)
        self.finished.emit(0)
