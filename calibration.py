# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CalibrationDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CalibrationDialog(object):
    def setupUi(self, CalibrationDialog):
        CalibrationDialog.setObjectName("CalibrationDialog")
        CalibrationDialog.resize(398, 354)
        CalibrationDialog.setStyleSheet("background-color: #1f232a;")
        self.gridLayout = QtWidgets.QGridLayout(CalibrationDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.widget_2 = QtWidgets.QWidget(CalibrationDialog)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pixelDistanceTextEdit = QtWidgets.QPlainTextEdit(self.widget_2)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.pixelDistanceTextEdit.setFont(font)
        self.pixelDistanceTextEdit.setLineWidth(3)
        self.pixelDistanceTextEdit.setReadOnly(True)
        self.pixelDistanceTextEdit.setCenterOnScroll(True)
        self.pixelDistanceTextEdit.setObjectName("pixelDistanceTextEdit")
        self.verticalLayout.addWidget(self.pixelDistanceTextEdit)
        self.knownDistanceTextEdit = QtWidgets.QPlainTextEdit(self.widget_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.knownDistanceTextEdit.setFont(font)
        self.knownDistanceTextEdit.setStyleSheet("color: rgb(255, 255, 255);")
        self.knownDistanceTextEdit.setInputMethodHints(QtCore.Qt.ImhDigitsOnly|QtCore.Qt.ImhFormattedNumbersOnly|QtCore.Qt.ImhPreferNumbers)
        self.knownDistanceTextEdit.setLineWidth(3)
        self.knownDistanceTextEdit.setObjectName("knownDistanceTextEdit")
        self.verticalLayout.addWidget(self.knownDistanceTextEdit)
        self.resultTextEdit = QtWidgets.QPlainTextEdit(self.widget_2)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.resultTextEdit.setFont(font)
        self.resultTextEdit.setLineWidth(3)
        self.resultTextEdit.setReadOnly(True)
        self.resultTextEdit.setCenterOnScroll(True)
        self.resultTextEdit.setObjectName("resultTextEdit")
        self.verticalLayout.addWidget(self.resultTextEdit)
        self.gridLayout.addWidget(self.widget_2, 0, 1, 1, 1)
        self.widget = QtWidgets.QWidget(CalibrationDialog)
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setStyleSheet("color: rgb(255, 255, 255);")
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.label_3 = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)
        self.okBtn = QtWidgets.QPushButton(CalibrationDialog)
        self.okBtn.setStyleSheet("color: rgb(255, 255, 255);")
        self.okBtn.setObjectName("okBtn")
        self.gridLayout.addWidget(self.okBtn, 1, 0, 1, 1)
        self.cancelBtn = QtWidgets.QPushButton(CalibrationDialog)
        self.cancelBtn.setStyleSheet("color: rgb(255, 255, 255);")
        self.cancelBtn.setObjectName("cancelBtn")
        self.gridLayout.addWidget(self.cancelBtn, 1, 1, 1, 1)

        self.retranslateUi(CalibrationDialog)
        QtCore.QMetaObject.connectSlotsByName(CalibrationDialog)

    def retranslateUi(self, CalibrationDialog):
        _translate = QtCore.QCoreApplication.translate
        CalibrationDialog.setWindowTitle(_translate("CalibrationDialog", "Calibration Dialog"))
        self.knownDistanceTextEdit.setPlaceholderText(_translate("CalibrationDialog", "Enter distance..."))
        self.label.setText(_translate("CalibrationDialog", "Distance in Pixels:"))
        self.label_2.setText(_translate("CalibrationDialog", "Known Distance (mm):"))
        self.label_3.setText(_translate("CalibrationDialog", "Pixel/mm Ratio:"))
        self.okBtn.setText(_translate("CalibrationDialog", "Ok"))
        self.cancelBtn.setText(_translate("CalibrationDialog", "Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CalibrationDialog = QtWidgets.QDialog()
    ui = Ui_CalibrationDialog()
    ui.setupUi(CalibrationDialog)
    CalibrationDialog.show()
    sys.exit(app.exec_())
