# !/usr/bin/env python3

"""

"""
from threading import Thread
import sys
from PyQt5.QtWidgets import QApplication
from web_gui import run_gui, MainWindow

def main():

    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
