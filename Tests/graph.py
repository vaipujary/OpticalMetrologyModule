from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(100))  # 100 time points
        self.y = [randint(0,100) for _ in range(100)]  # 100 data points

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first
        self.y.append(randint(0,100))  # Add a new random value.

        self.data_line.setData(self.x, self.y)  # Update the data.


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())







# class SimplePlot:
#     def __init__(self):
#         self.app = QApplication(sys.argv)
#         self.win = pg.GraphicsLayoutWidget(show=True, title="Simple Plot Example")
#         self.plot = self.win.addPlot(title="Dummy Data Over Time")
#         self.plot.setLabel('bottom', 'Time', units='s')
#         self.plot.setLabel('left', 'Value', units='units')
#         self.curve = self.plot.plot(pen='y')
#
#         self.data = []
#         self.time_data = []
#         self.start_time = time.time()
#
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.update)
#         self.timer.start(100)  # Update every 100 ms
#
#     def update(self):
#         current_time = time.time() - self.start_time
#         self.time_data.append(current_time)
#         self.data.append(np.sin(current_time))  # Dummy data: sine wave
#
#         self.curve.setData(self.time_data, self.data)
#         self.app.processEvents()
#
#     def run(self):
#         sys.exit(self.app.exec_())
#
# if __name__ == "__main__":
#     plot = SimplePlot()
#     plot.run()



# import pyqtgraph as pg
# import time
# from PyQt5.QtCore import QTimer
# from PyQt5.QtWidgets import QApplication
#
# from VideoProcessor import VideoProcessor
# from OpticalMetrologyModule import OpticalMetrologyModule
#
# # Create pyqtgraph application and plot widget (as before)
# app = pg.mkQApp("Particle Data Plotting")
# pw = pg.PlotWidget(title="Particle Size and Velocity")
# pw.addLegend()
# pw.setLabel('bottom', 'Time', units='s')
# pw.setLabel('left', 'Size', units='pixels')
#
# # Set right axis for Velocity
# pw.setLabel('right', 'Velocity', units='pixels/s')
# pw.showAxis('right')
#
# class MainProgram:
#     def __init__(self):
#
#         video_path = "../Test Data/Videos/MicrosphereVideo3.avi"
#
#         # Initialize video processor and metrology module
#         self.video_processor = VideoProcessor(ui_video_label=None, input_mode="file", video_source=video_path,
#                                         save_data_enabled=False)
#         self.optical_metrology_module = OpticalMetrologyModule(debug=False, fps=self.video_processor.fps)
#
#         # Set parent for plotting
#         self.video_processor.parent = self
#
#         self.size_curves = {}
#         self.velocity_curves = {}
#         self.start_time = time.time()
#         self.time_data = []
#
#         # Timer to process frames in real time
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.process_next_frame)
#         self.timer.start(int(1000 / self.video_processor.fps))
#
#     def process_next_frame(self):
#         """Process the next frame and update plots."""
#         self.video_processor.process_frame()
#         self.plot_data()
#         QApplication.processEvents()
#
#     def plot_data(self):
#             current_time = time.time() - self.start_time
#             self.time_data.append(current_time)
#
#             particle_ids = self.optical_metrology_module.microsphere_ids
#
#             for particle_id in particle_ids:
#                 size = self.optical_metrology_module.microsphere_sizes.get(particle_id, None)
#                 velocity = self.optical_metrology_module.microsphere_velocities.get(particle_id, None)
#
#                 if particle_id not in self.size_curves:
#                     self.size_curves[particle_id] = pw.plot(pen=pg.intColor(particle_id, len(particle_ids)),
#                                                        name=f'Size {particle_id}')
#                 if particle_id not in self.velocity_curves:
#                     self.velocity_curves[particle_id] = pw.plot(pen=pg.intColor(particle_id, len(particle_ids)),
#                                                            name=f'Velocity {particle_id}')
#
#                 if size is not None:
#                     self.size_curves[particle_id].setData(self.time_data, self.optical_metrology_module.microsphere_sizes[particle_id])
#                 if velocity is not None:
#                     self.velocity_curves[particle_id].setData(self.time_data,
#                                                          self.optical_metrology_module.microsphere_velocities[particle_id])
#
#
# if __name__ == "__main__":
#     program = MainProgram()
#
#     # Show the plot widget (if not already shown)
#     pw.show()
#
#     app.exec()
