from PyQt5.QtGui import *
from PyQt5.QtCore import *

import numpy as np
import pyqtgraph as pg
import random
import sys
import datetime
import sys
import numpy as np
import pyqtgraph as pg
# from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
from pyqtgraph import PlotWidget
from example import Ui_MainWindow
from PyQt5.QtWidgets import QLabel
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg
from pyqtgraph import PlotWidget


def main():
    # Optionally disable OpenGL if you suspect GPU issues
    pg.setConfigOptions(useOpenGL=False)

    app = QApplication(sys.argv)

    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            plot = PlotWidget()
            self.setCentralWidget(plot)
            # Just add some test data
            plot.plot([1, 2, 3, 4], [10, 20, 5, 15])

    w = TestWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

#
# class Window(QtWidgets.QMainWindow):
#
#     def __init__(self):
#         super(Window, self).__init__()
#         self.setWindowIcon(QIcon('pythonlogo.png'))
#         self.setGeometry(50,50,700,900)
#         self.home()
#
#     def home(self):
#
#         #Labels
#
#         staticLbl = QLabel("Static Plot",self)
#         staticLbl.move(10,50)
#
#         dynamicLbl = QLabel("Random Plot",self)
#         dynamicLbl.move(10,300)
#
#         conLbl = QLabel("Continuous Plot",self)
#         conLbl.move(10,550)
#
#         #Static plot widget:
#
#         staticPlt = pg.PlotWidget(self)
#         x = np.random.normal(size=10)
#         y = np.random.normal(size=10)
#
#         staticPlt.plot(x,y,clear=True)
#
#         staticPlt.move(200,50)
#         staticPlt.resize(450,200)
#
#         #Code to run to random plot using timer:
#
#         self.dynamicPlt = pg.PlotWidget(self)
#
#         self.dynamicPlt.move(200,300)
#         self.dynamicPlt.resize(450,200)
#
#         self.timer2 = pg.QtCore.QTimer()
#         self.timer2.timeout.connect(self.update)
#         self.timer2.start(200)
#
#         #Code to run to get continous plot using timer:
#
#         self.continuousPlt = pg.PlotWidget(self)
#
#         self.continuousPlt.move(200,550)
#         self.continuousPlt.resize(450,200)
#
#         self.timer3 = pg.QtCore.QTimer()
#         self.timer3.timeout.connect(self.cUpdate)
#         self.timer3.start(200)
#
#         self.show()
#
#     def update(self):
#         z = np.random.normal(size=1)
#         u = np.random.normal(size=1)
#         self.dynamicPlt.plot(z,u,pen=None, symbol='o')
#
#     def cUpdate(self):
#         now = datetime.datetime.now()
#         s = np.array([now.second])
#
#         self.continuousPlt.plot(s,s,pen=None, symbol='o')
#
#
# def run():
#         app=QtWidgets.QApplication(sys.argv)
#         GUI = Window()
#         sys.exit(app.exec_())
#
# run()
#




# #
# #
# class MainWindow(QtWidgets.QMainWindow):
#     def __init__(self):
#         super(MainWindow, self).__init__()
#         uic.loadUi("example.ui", self)
#         self.graphWidget = self.findChild(PlotWidget, "graphWidget")
#
#         self.graphWidget.showGrid(x=True, y=True)
#
#         self.show()
#
# def main():
#     app = QtWidgets.QApplication(sys.argv)
#     UIWindow = MainWindow()
#     app.exec_()
#
# if __name__ == "__main__":
#     main()


#         super().__init__()
#         self.ui = Ui_MainWindow()
#         self.ui.setupUi(self)
#         if self.ui.graphWidget is None:
#             print("Could not find graphGraphicsView")
#             sys.exit(1)
#
#         self.plot_graph = pg.PlotWidget(self.ui.graphWidget)
#         self.setCentralWidget(self.plot_graph)
#         time = [1,2,3,4,5,6,7,8,9,10]
#         temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 30]
#         self.plot_graph.plot(time, temperature)
#         # self.ui = Ui_MainWindow()
#         # self.ui.setupUi(self)
#         #
#         # if self.ui.graphWidget is None:
#         #     print("Could not find graphGraphicsView")
#         #     sys.exit(1)
#         #
#         # x = list(range(100))
#         # y = [i**0.5 for i in x]
#         #
#         # self.ui.graphWidget.setBackground('w')
#         # self.ui.graphWidget.setTitle("Example PyQtGraph")
#         # self.ui.graphWidget.setLabel("left", "Y Axis", color='red', size=30)
#         # self.ui.graphWidget.setLabel("bottom", "X Axis", color='blue', size=30)
#         # self.ui.graphWidget.plot(x, y, pen = "b", symbol = 'o', symbolBrush = 'r')
#
# app = QtWidgets.QApplication([])
# main = MainWindow()
# main.show()
# app.exec()
# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     main_window = MainWindow()
#     main_window.show()
#     sys.exit(app.exec_())