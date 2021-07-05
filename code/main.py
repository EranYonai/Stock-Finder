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
        # On initialization:
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint) # Remove titlebar
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # Remove titlebar ^^ Works!
        self.center()
        self.oldPos = self.pos()
        # Add Exit QAction to the

        # Triggers and connections:
        self.actionDay_Trading_Momentum.triggered.connect(self.momentum_page_open)
        self.actionTTM_Squeeze.triggered.connect(self.ttm_page_open)
        self.actionConsolidation_Patterns.triggered.connect(self.consolidation_page_open)
        self.actionExit.triggered.connect(self.close)


    def consolidation_page_open(self):
        self.stackedWidget.setCurrentIndex(2)

    def ttm_page_open(self):
        self.stackedWidget.setCurrentIndex(0)

    def momentum_page_open(self):
        self.stackedWidget.setCurrentIndex(1)

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()


# SPLASH SCREEN
class SplashScreen(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi(config.FILE_PATHS['SPLASH_UI'], self)


        ## REMOVE TITLE BAR
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # Center
        self.oldPos = self.pos()

        ## QTIMER ==> START
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(25)

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
            try:
                self.main = MainWindow()
                self.main.show()
            except Exception as e:
                print(e)
            # CLOSE SPLASH SCREEN
            self.close()

        counter += 1


    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = SplashScreen()
    win.show()
    win.setFocus()
    sys.exit(app.exec_())
