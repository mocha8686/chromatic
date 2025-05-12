#!/usr/bin/env python3

import sys
from PyQt6.QtWidgets import QApplication, QWidget


def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
