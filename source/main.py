import os.path
import random
import sys
import traceback
from pathlib import Path

from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QFont, QCursor, QMovie
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QAction, QDesktopWidget, QLabel, \
    QVBoxLayout, QFileDialog, QProgressBar, QHBoxLayout
from PyQt5.uic.properties import QtWidgets, QtCore

import Models
import ScrollLabel
from Compressor import Compressor, CompressState
from Config import Config
from CompressWorker import CompressWorker


class TinyRaccoon(QMainWindow):

    def __init__(self):
        super().__init__()
        self.thread = QThread()
        self.worker = CompressWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.onFinished)
        self.worker.image_file_signal.connect(self.onProgress)
        self.worker.err_signal.connect(self.onError)

        self.mainColor = '#1ee38d'
        self.mainColorDark = '#17bd75'
        self.backgroundColor = '#252a2e'
        self.darkSurfaceColor = '#181c1f'
        self.highlightColor = '#765eff'
        self.textColor = '#c0c7cf'
        self.initUI()
        self.setState(CompressState.IDLE)
        self.onUploadFile([])

        self.config = Config()
        self.worker.avg_quality = int(self.config.get('avg_quality', 80))

    def initUI(self):

        self.setWindowTitle("TinyDoge")
        self.setWindowIcon(QIcon('icon.png'))
        self.setStyleSheet(f'''
            color: {self.textColor};
            background-color: {self.backgroundColor};
        ''')

        self.widget = QWidget()
        self.vbox = QVBoxLayout(self.widget)

        self.setImageInputLayout()
        self.setProgressLayout()
        self.setFileNamesLayout()
        self.setCompressButtonLayout()

        self.setCentralWidget(self.widget)
        self.resize(900, 650)
        self.centerWindow()
        self.setToolBars()
        self.setAcceptDrops(True)
        self.show()

    def setImageInputLayout(self):
        vbox = QVBoxLayout()
        self.title = QLabel("TinyDoge\nImage Compressor")
        self.title.setFont(QFont('consolas', 18))
        self.title.setFixedHeight(100)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(f'''
            color: {self.highlightColor};
        ''')
        vbox.addWidget(self.title)

        self.btnImageUpload = QPushButton('&\n\nDrag Images Here or Click to Find\n\n', self)
        self.btnImageUpload.setFont(QFont('consolas'))
        self.btnImageUpload.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnImageUpload.setStyleSheet(f'''
            QPushButton {{
                background-color: {self.backgroundColor};
                border-radius: 16px;
                border: 2px dashed {self.mainColor};
                font-weight: bold;
                font-size: 20px;
                color: {self.mainColor};
            }}
            QPushButton:hover {{
                color: white;
                background-color: {self.darkSurfaceColor};
            }}
        ''')
        self.btnImageUpload.setCheckable(True)
        self.btnImageUpload.clicked.connect(self.showFileSelector)

        vbox.addWidget(self.btnImageUpload)
        self.vbox.addLayout(vbox)

    def setFileNamesLayout(self):
        self.fileNamesLabel = ScrollLabel.ScrollLabel()
        self.fileNamesLabel.setStyleSheet(f'''
            border-radius: 16px;
            background: {self.darkSurfaceColor}
        ''')
        self.fileNamesLabel.setTextStyleSheet(f'''
            font-family: consolas;
        ''')
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignTop)
        vbox.addSpacing(20)
        vbox.addWidget(self.fileNamesLabel)
        self.vbox.addLayout(vbox)

    def setCompressButtonLayout(self):
        self.btnCompress = QPushButton('&Compress', self)
        self.btnCompress.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnCompress.setStyleSheet(f'''
            QPushButton {{
                color: {self.backgroundColor};
                padding: 15px;
                border-radius: 16px;
                margin-top: 10px;
                font-size: 24px;
                background: {self.mainColor};
            }}
            QPushButton:hover {{
                background: {self.mainColorDark};
                color: white;
            }}
        ''')
        self.btnCompress.clicked.connect(self.onClickCompress)

        vbox = QVBoxLayout()
        tipsLabel = QLabel('* png를 제외한 나머지 확장자를 지원하지 않습니다.\n* 압축은 원본파일을 바로 덮어씁니다.\n* 손실압축이므로 여러번 압축하면 처참해질수있습니다.')
        tipsLabel.setFont(QFont('consolas', 10))
        vbox.addWidget(tipsLabel)
        vbox.addWidget(self.btnCompress)
        self.vbox.addLayout(vbox)

    def getRandomMovie(self):
        dg = random.choice([1, 1, 1, 2, 3, 4])
        dg_path = os.path.join(os.getcwd(), 'assets', f'doge{int(dg)}.gif')
        return QMovie(dg_path, QByteArray(), self)

    def setProgressLayout(self):
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        # dancing doge
        hbox2 = QHBoxLayout()
        self.dogeLabel = QLabel('Doge')
        self.dogeLabel.setFixedSize(100, 100)
        self.dogeLabel.setScaledContents(True)
        self.dogeLabel.setAlignment(Qt.AlignCenter)
        hbox2.addWidget(self.dogeLabel)
        vbox.addLayout(hbox2)

        # progress state textviews
        self.processingTitle = QLabel('Processing')
        self.processingTitle.setStyleSheet(f'''
            font-family: consolas;
            font-weight: bold;
            color: {self.mainColor};
        ''')
        hbox.addWidget(self.processingTitle)
        self.processingFileLabel = QLabel('filename')
        self.processingFileLabel.setAlignment(Qt.AlignRight)
        hbox.addWidget(self.processingFileLabel)
        vbox.addLayout(hbox)

        # progresbar
        self.progressBar = QProgressBar()
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setStyleSheet(f'''
            QProgressBar {{
                background-color: {self.darkSurfaceColor};
                border: none;
                border-radius: 46px;
                text-align: center;
                font-family: consolas;
            }}
            QProgressBar::chunk {{
                background-color: {self.highlightColor};
                border-radius: 6px;
            }}
        ''')
        vbox.addWidget(self.progressBar)
        self.vbox.addLayout(vbox)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            files = [u.toLocalFile() for u in event.mimeData().urls()]
            self.onUploadFile(files)
            event.accept()
        else:
            event.ignore()

    def onUploadFile(self, files: list):
        if len(files) == 0:
            self.image_files = []
            self.fileNamesLabel.label.setAlignment(Qt.AlignCenter)
            self.fileNamesLabel.setText("이미지를 업로드 해주세요")
        else:
            self.fileNamesLabel.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.image_files = []
            # png 파일만 더한다.
            for (i, file) in enumerate(files):
                fn, ext = os.path.splitext(file)
                if ext.lower() == '.png':
                    self.image_files.append(Models.ImageFile(
                        id=i,
                        filename=os.path.abspath(file),
                        size=os.path.getsize(file),
                        result_size=0
                    ))
            filenames = "\n".join([f"{i+1}. {x.filename}" for i, x in enumerate(self.image_files)])
            self.fileNamesLabel.setText(
                f'''
                첨부한 이미지 수: {len(self.image_files)}\n{filenames}
                '''.lstrip().rstrip()
            )

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setToolBars(self):
        openFile = QAction(QIcon('open.png'), 'Upload images', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Upload images')
        openFile.triggered.connect(self.showFileSelector)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)

    def showFileSelector(self):
        recent_path = self.config.get('recent_path', '')

        if len(recent_path) == 0 or not os.path.exists(recent_path):
            recent_path = os.path.join(os.path.expanduser('~'), 'Downloads')
            self.config.set('recent_path', recent_path)

        files = QFileDialog.getOpenFileNames(self, '이미지 선택', recent_path, 'Image Files(*.png)')
        if files:
            if len(files[0]) > 0:
                self.config.set('recent_path', str(Path(files[0][0]).parent))
            self.onUploadFile(files[0])

    def onClickCompress(self):
        if self.__state == CompressState.COMPRESSING:
            self.stopCompress()
        else:
            self.compressImages()

    def compressImages(self):
        if len(self.image_files) > 0 and self.__state == CompressState.IDLE:
            self.setState(CompressState.COMPRESSING)
            self.worker.image_files = self.image_files
            self.thread.start()

    def stopCompress(self):
        self.worker.finished.emit(1)

    def setState(self, state):
        self.__state = state
        processingViews = [
            self.processingTitle,
            self.processingFileLabel,
            self.progressBar
        ]
        if self.__state == CompressState.IDLE:
            self.fileNamesLabel.setEnabled(True)
            for v in processingViews:
                v.hide()
            self.btnImageUpload.setFixedHeight(120)
            self.btnImageUpload.setAutoFillBackground(True)
            self.btnImageUpload.show()
            self.dogeLabel.hide()
            self.btnCompress.setText("Compress")
        if self.__state == CompressState.COMPRESSING:
            self.fileNamesLabel.setEnabled(False)
            self.title.setText(f"Doge's busy now")
            movie = self.getRandomMovie()
            self.dogeLabel.setMovie(movie)
            movie.start()
            self.dogeLabel.show()
            self.progressBar.setValue(0)
            self.btnImageUpload.setFixedHeight(0)
            self.btnImageUpload.hide()
            self.btnCompress.setText("Stop")
            for v in processingViews:
                v.show()

    def onError(self, ex: BaseException):
        self.onUploadFile([])
        self.setState(CompressState.IDLE)
        self.title.setText(f"Sorry...Error!\n{str(ex)}")

    def onFinished(self, exit_code: int):
        try:
            if exit_code != 0:
                raise Exception("Interrupted")
            original = sum(f.size for f in self.image_files)
            result = sum(f.result_size for f in self.image_files)
            save_rate = 100 - (100 * result / original)

            self.title.setText(f'Completed!\nYou saved {int(save_rate)}% for {len(self.image_files)} images.')
        except Exception as e:
            self.title.setText('Doge knows when to stop :)')
        finally:
            self.onUploadFile([])
            self.setState(CompressState.IDLE)


    def onProgress(self, image_file: Models.ImageFile):
        try:
            self.image_files[image_file.id] = image_file
            self.progressBar.setValue(int((image_file.id + 1) / len(self.image_files) * 100))
            self.processingFileLabel.setText(Path(image_file.filename).name)
        except IndexError as e:
            pass


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error catched!:")
    print("error message:\n", tb)
    QtWidgets.QApplication.quit()
    # or QtWidgets.QApplication.exit(0)


if __name__ == '__main__':
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    ex = TinyRaccoon()
    sys.exit(app.exec_())
