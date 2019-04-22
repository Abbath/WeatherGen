from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtCore import pyqtSignal, Qt, QLocale

from ui_weather_gen import Ui_WeatherGen
from weather_gen import process, diff_link

import sys
import threading
import locale

class WeatherGen(QMainWindow):
    logg = pyqtSignal(str)
    def __init__(self):
        super(WeatherGen, self).__init__()

        self.ui = Ui_WeatherGen()
        self.ui.setupUi(self)

        self.ui.select.clicked.connect(self.select)
        self.ui.select1.clicked.connect(self.select1)
        self.ui.generate.clicked.connect(self.generate)
        self.logg.connect(self.trueLog, Qt.QueuedConnection)

        self.running = False

    def select(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save .dat file", "", "DAT files (*.dat)")
        if filename:
            self.ui.output.setText(filename)
        
    def select1(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open .dat file", "", "DAT files (*.dat)")
        if filename:
            self.ui.dat.setText(filename)

    def generate(self):
        if not self.running:
            link = self.ui.link.text()
            output = self.ui.output.text()
            dat = self.ui.dat.text()
            if link and output and (dat or diff_link(link) == 2):
                self.running = True
                t = threading.Thread(target=process, args=[link, output, dat, self.log, True, self.ui.second.checkState(), self.ui.remtags.checkState()])
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

