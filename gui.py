from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtCore import pyqtSignal, Qt

from ui_weather_gen import Ui_WeatherGen
from weather_gen import process

import sys
import threading

class WeatherGen(QMainWindow):
    logg = pyqtSignal(str)
    def __init__(self):
        super(WeatherGen, self).__init__()

        self.ui = Ui_WeatherGen()
        self.ui.setupUi(self)

        self.ui.select.clicked.connect(self.select)
        self.ui.generate.clicked.connect(self.generate)
        self.logg.connect(self.trueLog, Qt.QueuedConnection)

        self.running = False

    def select(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save .dat file", "", "DAT files (*.dat)")
        if filename:
            self.ui.output.setText(filename)

    def generate(self):
        if not self.running:
            link = self.ui.link.text()
            output = self.ui.output.text()
            if link and output:
                self.running = True
                t = threading.Thread(target=process, args=[link, output, self.log, True])
                t.start()

    def log(self, text):
        self.logg.emit(text)

    def trueLog(self, text):
        if 'Report generated.' in text:
            self.running = False
        self.ui.log.appendPlainText(text)
        self.ui.log.update()

def main():
    app = QApplication(sys.argv)
    wg = WeatherGen()
    wg.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

