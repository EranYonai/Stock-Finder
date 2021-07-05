import sys
import platform
from PyQt5 import QtWidgets, uic, QtGui, QtCore, Qt
import config
import yfinance as yf
import yf_functions as yf_func

## ==> GLOBALS
counter = 0


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(config.FILE_PATHS['MAIN_UI'], self)
        # On initialization:
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint) # Remove titlebar
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # Remove titlebar ^^ Works!
        self.center()
        self.oldPos = self.pos()
        self.consolidation_bar.hide()

        # Global Attributes:
        self.data_1d_exists = False

        # Triggers and connections:
        self.actionDay_Trading_Momentum.triggered.connect(self.momentum_page_open)
        self.actionTTM_Squeeze.triggered.connect(self.ttm_page_open)
        self.actionConsolidation_Patterns.triggered.connect(self.consolidation_page_open)
        self.actionExit.triggered.connect(self.close)
        self.analyze_button_2.clicked.connect(self.consolidation_scan)


    def consolidation_page_open(self):
        self.stackedWidget.setCurrentIndex(2)


    def consolidation_scan(self):
        tickers = yf_func.load_tickers_from_ini()
        percentage = float(self.percentage_text.text())
        lookback = int(self.lookback_text.text())

        self.consolidation_bar.show()
        self.consolidation_bar.setValue(0)
        total_for_bar = 100/len(tickers)
        counter = 1
        tickers_data = {}

        for ticker in tickers:
            df = yf.download(ticker)  # Need to download all to csv and use that
            if yf_func.is_consolidating(df, percentage=percentage, look_back_data=lookback):
                self.results_edit_2.append(f'{ticker} is consolidating')
            if yf_func.is_breaking_consolidation(df, percentage=percentage, look_back_data=lookback):
                self.results_edit_2.append(f'{ticker} is breaking out of consolidation!')
            self.consolidation_bar.setValue(int(total_for_bar * counter))
            counter += 1


    def download_updated_data_to_csv(self):
        ticker_list = yf_func.load_tickers_from_ini()
        data = yf.download(
            tickers=ticker_list,
            period='1y',
            interval='1d',
            group_by='ticker',
            auto_adjust=False,
            prepost=False,
            threads=True,
            proxy=None
        )
        data = data.T
        for ticker in ticker_list:
            data.loc[(ticker,),].T.to_csv(config.FILE_PATHS['1D_DATA'] + ticker + '.csv', sep=',', encoding='utf-8')
        self.data_1d_exists = True


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
        self.timer.start(10)

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
