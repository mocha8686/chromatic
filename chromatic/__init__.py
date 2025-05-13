from math import log10
from PyQt6.QtCore import QTimer
import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget
import pyaudio
import numpy as np


class MainWindow(QMainWindow):
    freq = []
    data = []

    def __init__(self) -> None:
        super().__init__()

        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.seconds = 3

        self.freq = np.fft.rfftfreq(self.chunk, d=1.0 / self.rate)

        self.graph = pg.GraphicsLayoutWidget()

        self.plot = self.graph.addPlot()
        # self.plot.setXRange(1, log10(20000))
        self.plot.setYRange(0, 1)
        self.plot.setMouseEnabled(x=False, y=False)
        # self.plot.setLogMode(x=True)

        self.button = QPushButton("Start recording")
        self.button.clicked.connect(self.start_recording)

        layout = QVBoxLayout()
        layout.addWidget(self.graph)
        layout.addWidget(self.button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.line = self.plot.plot(self.freq, self.data)
        # self.line.setLogMode(xState=True, yState=False)

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
        data_frame = np.fromstring(data, "int16") / 32_768

        self.data = np.fft.rfft(data_frame, self.chunk)
        self.data = self.data / np.abs(self.data).max()
        # self.data[0] = 0

        self.line.setData(self.freq, np.abs(self.data))
        # self.plot.setXRange(log10(max(20, self.freq[1])), log10(20000))

        if self.stop:
            return None, pyaudio.paComplete
        return None, pyaudio.paContinue
