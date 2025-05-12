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

        self.button = QPushButton("Start recording")
        self.button.clicked.connect(self.start_recording)

        layout = QVBoxLayout()
        layout.addWidget(self.graph)
        layout.addWidget(self.button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.line = self.graph.plot(self.time, self.data)

    def start_recording(self):
        self.button.setText("Stop recording")
        self.button.clicked.connect(self.stop_recording)

        self.stop = False
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            frames_per_buffer=self.chunk,
            input=True,
            stream_callback=self.new_frame,
        )

    def stop_recording(self):
        self.stop = True
        self.stream.close()
        self.p.terminate()
        self.button.setText("Start recording")
        self.button.clicked.connect(self.start_recording)

    def new_frame(self, data, frame_count, time_info, status):
        self.data = np.fromstring(data, 'int16') / 32_768
        self.line.setData(self.time, self.data)

        if self.stop:
            return None, pyaudio.paComplete
        return None, pyaudio.paContinue
