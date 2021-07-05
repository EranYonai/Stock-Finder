import sys
import platform
from PyQt5 import QtWidgets, uic, QtGui, QtCore, Qt
import config

## ==> GLOBALS
counter = 0


# YOUR APPLICATION
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(config.FILE_PATHS['MAIN_UI'], self)

        # Triggers and connections:
        self.analyze_button.clicked.connect(self.say_hello)
        self.actionDay_Trading_Momentum.triggered.connect(self.momentum_page)
        self.actionTTM_Squeeze.triggered.connect(self.ttm_page)

    def say_hello(self):
        print("Hello")

    def ttm_page(self):
        try:
            self.stackedWidget.setCurrentIndex(0)
        except Exception as e:
            print(e)

    def momentum_page(self):
        self.stackedWidget.setCurrentIndex(1)


# SPLASH SCREEN
class SplashScreen(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi(config.FILE_PATHS['SPLASH_UI'], self)

        ## UI ==> INTERFACE CODES
        ########################################################################

        ## REMOVE TITLE BAR
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        ## QTIMER ==> START
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(35)

        # CHANGE DESCRIPTION
        self.timer.singleShot(1500, lambda: self.label_description.setText("<strong>LOADING</strong> FUNCTIONS"))
        self.timer.singleShot(3000,
                              lambda: self.label_description.setText("<strong>LOADING</strong> USER INTERFACE"))
        # Initial Text
        self.label_description.setText("<strong>Stock Finding</strong> Algorithms")

        ## SHOW ==> MAIN WINDOW
        self.show()

    ## ==> APP FUNCTIONS
    ########################################################################
    def progress(self):
        global counter
        # SET VALUE TO PROGRESS BAR
        self.progressBar.setValue(counter)

        # CLOSE SPLASH SCREE AND OPEN APP
        if counter > 100:
            self.timer.stop()
            # SHOW MAIN WINDOW
            self.main = MainWindow()
            self.main.show()
            # CLOSE SPLASH SCREEN
            self.close()

        counter += 1


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = SplashScreen()
    win.show()
    win.setFocus()
    sys.exit(app.exec_())
