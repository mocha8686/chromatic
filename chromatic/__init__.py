from PyQt6.QtCore import QTimer
import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget
import pyaudio
import numpy as np


class MainWindow(QMainWindow):
    time = [i + 1 for i in range(1024)]
    data = [0 for _ in range(1024)]

    def __init__(self) -> None:
        super().__init__()

        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.seconds = 3

        self.graph = pg.PlotWidget()
        self.graph.setYRange(-1, 1)

        self.button = QPushButton("Record")
        self.button.clicked.connect(self.start_recording)

        layout = QVBoxLayout()
        layout.addWidget(self.graph)
        layout.addWidget(self.button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.line = self.graph.plot(self.time, self.data)

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: print('Hi'))
        self.timer.start(1000)

    def start_recording(self):
        self.button.setEnabled(False)

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            frames_per_buffer=self.chunk,
            input=True,
        )

        for _ in range(0, self.rate // self.chunk * self.seconds):
            raw_data = self.stream.read(self.chunk)
            arr = np.frombuffer(raw_data, dtype='>i2') / 32_768
            self.data = arr
            self.line.setData(self.time, self.data)

        self.stream.close()
        self.p.terminate()
        self.button.setEnabled(True)
