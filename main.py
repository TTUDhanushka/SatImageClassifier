# !/usr/bin/env python3

"""

"""
from threading import Thread
import sys
from PyQt5.QtWidgets import QApplication
from web_gui import run_gui, MainWindow

def main():

    # ui_thread = Thread(target=run_gui)
    #
    # ui_thread.start()
    app = QApplication(sys.argv)
    # app.setAttribute(Qt.AA_EnableHighDpiScaling)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
