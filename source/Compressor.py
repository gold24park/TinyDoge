import os
import platform
import shutil
import threading
import time
from enum import Enum
from pathlib import Path
from typing import Callable
import subprocess

from PyQt5.QtCore import *

class CompressState(Enum):
    IDLE = 0
    COMPRESSING = 1
    COMPRESSED = 2


class Compressor:

    def __init__(self):
        platform_name = platform.system()
        pngquant_path = os.path.join(os.getcwd(), 'pngquant')
        self.temp_path = os.path.join(os.getcwd(), 'tmp_image')
        if not os.path.exists(self.temp_path):
            os.mkdir(self.temp_path)
        if platform_name == 'Windows':
            self.quant_file = os.path.join(pngquant_path, 'windows', 'pngquant.exe')
        if platform_name == 'Darwin':
            self.quant_file = os.path.join(pngquant_path, 'macos', 'pngquant')

    def compress(self, avg_quality: int, image_files: list, image_file_signal, err_signal):
        if avg_quality == 0:
            avg_quality = 80 # default
        avg_quality = max(avg_quality, 0)
        avg_quality = min(avg_quality, 100)
        self.q = avg_quality

        try:
            # 한글깨짐때문에 넣음
            os.system('chcp 65001')
            os.system('dir/w')

            temp_files = [
                os.path.join(self.temp_path, 'image1.png'),
                os.path.join(self.temp_path, 'image2.png'),
                os.path.join(self.temp_path, 'image3.png')
            ]

            for tmp in temp_files:
                Path(tmp).touch()

            for index, image_file in enumerate(image_files):
                # shell True 해줘야 console이 안보인다.
                subprocess.run(fr'{self.quant_file} --floyd=0.32 --posterize=1 --speed=1 --quality={max(self.q - 20, 20)}-{min(self.q + 5, 100)} --strip --force -o {temp_files[0]} "{image_file.filename}"', shell=True)
                subprocess.run(fr'{self.quant_file} --floyd=0.45 --speed=1 --quality={max(self.q - 30, 20)}-{self.q} --strip --force -o {temp_files[1]} "{image_file.filename}"', shell=True)
                subprocess.run(fr'{self.quant_file} --floyd=0.2 --speed=1 --quality={min(self.q + 10, 100)} --strip --force -o {temp_files[2]} "{image_file.filename}"', shell=True)

                sizes = [os.path.getsize(f) for f in temp_files]
                min_size = min(sz for sz in sizes if sz > 0)

                if min_size / 1024 < 1 or min_size >= image_files[index].size:
                    # 압축한게 더 별로라면 오리지널 놔둠.
                    min_size = image_files[index].size
                else:
                    best_idx = sizes.index(min_size)
                    shutil.copy(temp_files[best_idx], image_file.filename)

                image_files[index].result_size = min_size
                image_file_signal.emit(image_file)

            for tmp in temp_files:
                try:
                    os.remove(tmp)
                    pass
                finally:
                    pass
        except BaseException as e:
            err_signal.emit(e)
