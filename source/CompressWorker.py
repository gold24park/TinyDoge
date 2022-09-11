import traceback
from collections.abc import Callable

from PyQt5.QtCore import *

from Compressor import Compressor
from Models import ImageFile, ExitObject


class CompressWorker(QObject):
    image_file_signal = pyqtSignal(ImageFile)
    finished = pyqtSignal(ExitObject)  # if int != 0: Interrupted

    def __init__(self):
        super().__init__()
        self.compressor = Compressor()
        self.avg_quality = 0
        self.image_files = list()

    def run(self):
        try:
            self.compressor.compress(
                avg_quality=self.avg_quality,
                image_files=self.image_files,
                image_file_signal=self.image_file_signal
            )
            QThread.sleep(1)
            self.finished.emit(ExitObject())
        except Exception as e:
            traceback.print_exc()
            self.finished.emit(ExitObject(code=2, exception=e))
