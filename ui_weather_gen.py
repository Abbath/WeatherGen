# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'weather_gen.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WeatherGen(object):
    def setupUi(self, WeatherGen):
        WeatherGen.setObjectName("WeatherGen")
        WeatherGen.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(WeatherGen)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.output = QtWidgets.QLineEdit(self.centralwidget)
        self.output.setObjectName("output")
        self.gridLayout.addWidget(self.output, 1, 1, 1, 1)
        self.select = QtWidgets.QPushButton(self.centralwidget)
        self.select.setObjectName("select")
        self.gridLayout.addWidget(self.select, 1, 2, 1, 1)
        self.generate = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.generate.sizePolicy().hasHeightForWidth())
        self.generate.setSizePolicy(sizePolicy)
        self.generate.setObjectName("generate")
        self.gridLayout.addWidget(self.generate, 3, 0, 1, 3)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.link = QtWidgets.QLineEdit(self.centralwidget)
        self.link.setObjectName("link")
        self.gridLayout.addWidget(self.link, 0, 1, 1, 2)
        self.log = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.log.setObjectName("log")
        self.gridLayout.addWidget(self.log, 4, 0, 1, 3)
        self.select1 = QtWidgets.QPushButton(self.centralwidget)
        self.select1.setObjectName("select1")
        self.gridLayout.addWidget(self.select1, 2, 2, 1, 1)
        self.dat = QtWidgets.QLineEdit(self.centralwidget)
        self.dat.setObjectName("dat")
        self.gridLayout.addWidget(self.dat, 2, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        WeatherGen.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(WeatherGen)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 28))
        self.menubar.setObjectName("menubar")
        WeatherGen.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(WeatherGen)
        self.statusbar.setObjectName("statusbar")
        WeatherGen.setStatusBar(self.statusbar)

        self.retranslateUi(WeatherGen)
        QtCore.QMetaObject.connectSlotsByName(WeatherGen)

    def retranslateUi(self, WeatherGen):
        _translate = QtCore.QCoreApplication.translate
        WeatherGen.setWindowTitle(_translate("WeatherGen", "WeatherGen"))
        self.label.setText(_translate("WeatherGen", "Link"))
        self.select.setText(_translate("WeatherGen", "Select"))
        self.generate.setText(_translate("WeatherGen", "GENERATE"))
        self.label_2.setText(_translate("WeatherGen", "Output"))
        self.select1.setText(_translate("WeatherGen", "Select"))
        self.label_3.setText(_translate("WeatherGen", "Dat"))

