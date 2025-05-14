from enum import Enum
from math import log10
from PyQt6 import QtCore
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)
import pyaudio
import numpy as np


class Mode(Enum):
    SPECTRUM = 1
    WAVEFORM = 2

    def __str__(self) -> str:
        match self:
            case Mode.SPECTRUM:
                return "Spectrum"
            case Mode.WAVEFORM:
                return "Waveform"


class MainWindow(QMainWindow):
    x_axis = []
    y_axis = []
    request_graph_update = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Chromatic")

        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.seconds = 3
        self.gain = 0

        self.request_graph_update.connect(self.update_line)

        self.graph = pg.GraphicsLayoutWidget()

        self.plot = self.graph.addPlot()
        self.plot.setMouseEnabled(x=False, y=False)
        self.plot.hideButtons()

        self.gain_label = QLabel("Gain")
        self.gain_slider = QSlider(Qt.Orientation.Horizontal)
        self.gain_slider.valueChanged.connect(self.set_gain)

        gain_layout = QHBoxLayout()
        gain_layout.addWidget(self.gain_label)
        gain_layout.addWidget(self.gain_slider)

        self.record_button = QPushButton("Start recording")
        self.record_button.clicked.connect(self.start_recording)

        self.mode = Mode.SPECTRUM
        self.mode_button = QPushButton(str(self.mode))
        self.mode_button.setCheckable(True)
        self.mode_button.setChecked(True)
        self.mode_button.clicked.connect(self.toggle_mode)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.record_button)
        button_layout.addWidget(self.mode_button)

        layout = QVBoxLayout()
        layout.addWidget(self.graph)
        layout.addLayout(gain_layout)
        layout.addLayout(button_layout)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.line = self.plot.plot(self.x_axis, self.y_axis)
        # self.line.setLogMode(xState=True, yState=False)

    def start_recording(self):
        self.record_button.setText("Stop recording")
        self.record_button.clicked.connect(self.stop_recording)

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

    def toggle_mode(self, is_spectrum):
        if is_spectrum:
            self.mode = Mode.SPECTRUM
        else:
            self.mode = Mode.WAVEFORM

        self.mode_button.setText(str(self.mode))

    def stop_recording(self):
        self.stop = True
        self.stream.close()
        self.p.terminate()
        self.record_button.setText("Start recording")
        self.record_button.clicked.connect(self.start_recording)

    def new_frame(self, data, frame_count, time_info, status):
        data_frame = np.fromstring(data, "int16")

        match self.mode:
            case Mode.SPECTRUM:
                amplitude = np.fft.rfft(data_frame, self.chunk)
                amplitude *= (1 + self.gain) / 5000000.0
                amplitude = np.abs(amplitude)
                self.y_axis = amplitude

                frequency = np.fft.rfftfreq(self.chunk, d=1.0 / self.rate)
                frequency[0] = 20
                self.x_axis = frequency

            case Mode.WAVEFORM:
                amplitude = data_frame / 32_768
                self.y_axis = amplitude

                time = np.arange(1024)
                self.x_axis = time

        self.set_graph_settings()
        self.request_graph_update.emit()

        if self.stop:
            return None, pyaudio.paComplete
        return None, pyaudio.paContinue

    def set_gain(self, gain: int):
        print(gain)
        self.gain = gain

    def update_line(self):
        self.line.setData(self.x_axis, self.y_axis)

    def set_graph_settings(self):
        match self.mode:
            case Mode.SPECTRUM:
                self.plot.setXRange(log10(20), log10(20000))
                self.plot.setYRange(0, 1)
                self.plot.showGrid(x=True, y=True, alpha=0.4)
                self.plot.setLogMode(x=True)

                ax = self.plot.getAxis("bottom")
                ticks_list = [
                    (20, "20"),
                    (50, "50"),
                    (100, "100"),
                    (200, "200"),
                    (500, "500"),
                    (1000, "1k"),
                    (2000, "2k"),
                    (5000, "5k"),
                    (10000, "10k"),
                    (20000, "20k"),
                ]
                ax.setTicks(
                    [
                        [(log10(val), str) for val, str in ticks_list],
                        [],
                    ]
                )

            case Mode.WAVEFORM:
                self.plot.setXRange(0, 1024)
                self.plot.setYRange(-1, 1)
                self.plot.showGrid(x=True, y=True, alpha=0.4)
                self.plot.setLogMode(x=False)

                ax = self.plot.getAxis("bottom")
                ticks_list = [(n, str(n)) for n in range(0, 1024, 1024 // 4)]
                ax.setTicks(
                    [
                        ticks_list,
                        [],
                    ]
                )
