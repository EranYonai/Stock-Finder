import sys
import platform
from PyQt5 import QtWidgets, uic, QtGui, QtCore, Qt
import config
import yfinance as yf
import pandas as pd
import yf_functions as yf_func
from datetime import datetime
import configparser, os.path, glob, traceback

## ==> GLOBALS
counter = 0


# Global methods:

def set_ini_date(date=None):
    """
    Update ini file 1d date sections
    :param date: date to update, if None enter the current date
    :type date: str
    """
    if date == None:
        date = datetime.today().strftime('%Y-%d-%m')
    cp = configparser.ConfigParser()
    cp.read(config.FILE_PATHS['INI'])
    cp.set(config.INI_SECTIONS['DATA'], config.INI_DATA['1D'], date)
    with open(config.FILE_PATHS['INI'], 'w') as configfile:
        cp.write(configfile)


def get_ini_date() -> str:
    """
    get date from ini file
    :return: date in %y-%d-%m format
    :rtype: str
    """
    cp = configparser.ConfigParser()
    cp.read(config.FILE_PATHS['INI'])
    return cp.get(config.INI_SECTIONS['DATA'], config.INI_DATA['1D'])


def dir_is_empty(dir: str) -> bool:
    """
    checks if a directory is empty
    :param dir: dir path with // in the end
    :type dir: str
    :return: true if empty, false if not
    :rtype: bool
    """
    files = glob.glob(dir + '*')
    if len(files) >= 1:
        return False
    return True


class MainWindow(QtWidgets.QMainWindow):
    """
    Main dialog of the application
    """

    def __init__(self):
        """
        init - initialize on dialog call.
        """
        super(MainWindow, self).__init__()
        uic.loadUi(config.FILE_PATHS['MAIN_UI'], self)
        # On initialization:
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # Remove titlebar
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # Remove titlebar ^^ Works!
        self.center()
        self.oldPos = self.pos()
        self.consolidation_bar.hide()
        self.short_long_label.hide()
        self.short_long_label_2.hide()

        # Global Attributes:
        self.data_1d_exists = False

        # Triggers and connections:
        self.actionDay_Trading_Momentum.triggered.connect(self.momentum_page_open)
        self.actionTTM_Squeeze.triggered.connect(self.ttm_page_open)
        self.actionConsolidation_Patterns.triggered.connect(self.consolidation_page_open)
        self.actionManual_Risk_Calculator.triggered.connect(self.manual_risk_open)
        self.actionExit.triggered.connect(self.close)
        self.analyze_button_2.clicked.connect(self.consolidation_scan)
        self.analyze_button_3.clicked.connect(self.momentum_ticker)
        self.riskcalculate_button.clicked.connect(self.manual_risk)

    def consolidation_page_open(self):
        """
        change stackedWidget to consolidation page
        :return:
        :rtype:
        """
        self.stackedWidget.setCurrentIndex(2)

    def consolidation_scan(self):
        """
        On 'analiyze_button' press - scans for consolidation patterns in ini tickers.
        :return:
        :rtype:
        """
        tickers = yf_func.load_tickers_from_ini()  # load tickers from ini
        percentage = float(self.percentage_text.text())  # get percentage from textbox
        lookback = int(self.lookback_text.text())  # get lookback (days to look for consolidation) from textbox

        self.consolidation_bar.show()  # show the bar
        self.consolidation_bar.setValue(0)  # start progress bar from zero
        total_for_bar = 100 / len(tickers)  # each ticker is a % of the total 100%
        counter = 1
        date = datetime.today().strftime('%Y-%d-%m')  # current date
        try:
            if not (get_ini_date() == date) or dir_is_empty(
                    config.FILE_PATHS['1D_DATA']):  # not(date) or empty | is material implication
                self.download_updated_data_to_csv()  # download tickers data to csv at code/data/1D
                set_ini_date(date)  # set ini date to current date for future reference
            self.results_edit_2.setText('')  # clears text edit.
            for ticker in tickers:
                df = pd.read_csv(config.FILE_PATHS['1D_DATA'] + ticker + '.csv')  # read from csv file to df
                if yf_func.is_consolidating(df, percentage=percentage, look_back_data=lookback):
                    self.results_edit_2.append(f'{ticker} is consolidating')
                if yf_func.is_breaking_consolidation(df, percentage=percentage, look_back_data=lookback):
                    self.results_edit_2.append(f'{ticker} is breaking out of consolidation!')
                self.consolidation_bar.setValue(int(total_for_bar * counter))  # update bar
                counter += 1
        except Exception as e:
            print(e)
            traceback.print_exc()

    def download_updated_data_to_csv(self):
        """
        download updated tickers data using yfinance.download threaded.
        :return:
        :rtype:
        """
        ticker_list = yf_func.load_tickers_from_ini()  # get tickers list.
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
        data = data.T  # switch columns and rows for df
        if not dir_is_empty(config.FILE_PATHS['1D_DATA']):  # if the directory is not empty, delete all csv files.
            files = glob.glob(config.FILE_PATHS['1D_DATA'] + '\*.csv')
            for f in files:
                os.remove(f)
        try:  # verify that the directory exists, if not, create it.
            os.makedirs(config.FILE_PATHS['1D_DATA'])
        except Exception as e:
            traceback.print_exc()

        for ticker in ticker_list:  # insert df data to csv files.
            f = open(config.FILE_PATHS['1D_DATA'] + ticker + '.csv', 'w')
            data.loc[(ticker,),].T.to_csv(config.FILE_PATHS['1D_DATA'] + ticker + '.csv', sep=',', encoding='utf-8')

        set_ini_date()  # set the current day to ini file
        self.data_1d_exists = True  # not used...

    def ttm_page_open(self):
        """
        change stackedWidget to ttm page
        :return:
        :rtype:
        """
        self.stackedWidget.setCurrentIndex(0)

    def momentum_page_open(self):
        """
        change stackedWidget to momentum page
        :return:
        :rtype:
        """
        self.stackedWidget.setCurrentIndex(1)

    def manual_risk_open(self):
        """
        change stackedWidget to Manual Risk Calculator
        :return:
        :rtype:
        """
        self.stackedWidget.setCurrentIndex(3)

    def manual_risk(self):
        """
        Calculate manual risk
        :return:
        :rtype:
        """
        entry_price = float(self.entryprice_edit.text())
        protective_stop = float(self.stoploss_edit.text())
        risk = float(self.risk_edit.text())
        risk_result = yf_func.risk_dict(risk=risk, risk_candle=entry_price-protective_stop,
                                        current_stock_price=entry_price)
        string_result = yf_func.dumb_risk_analysis_tostring(risk_dict=risk_result)

        if risk_result['SHORT/LONG'] == 'LONG':
            self.short_long_label_2.setStyleSheet('background-color: rgb(24, 124, 41)')
            self.short_long_label_2.setText('Long')
            self.short_long_label_2.show()
        else:
            self.short_long_label_2.setStyleSheet('background-color: rgb(193, 44, 44)')
            self.short_long_label_2.setText('Short')
            self.short_long_label_2.show()
        self.results_edit_4.setText(string_result)
        # Problem with logic when shorting


    def momentum_ticker(self):
        """
        Shows calculation of risk_dict of a certain ticker, with certain risk (taken from textboxes)
        :return:
        :rtype:
        """
        self.results_edit_3.setText('')
        try:
            risk_analysis = yf_func.risk_analysis(yf.Ticker(self.ticker_text.text()), int(self.risk_text.text()))
            risk_answer = risk_analysis
            if not yf_func.trading_day_started():
                self.results_edit_3.append(
                    "Risk candle is based on GAP since data on the first candle of the day is unavailable.")
            self.results_edit_3.append(yf_func.dumb_risk_analysis_tostring(risk_answer))
            df = pd.read_csv(config.FILE_PATHS['1D_DATA'] + self.ticker_text.text() + '.csv')
            sma = [20, 50, 100, 200]
            for i in sma:
                self.results_edit_3.append(f'SMA {str(i)}: {yf_func.get_SMA(df, i)}')
            self.results_edit_3.append(f'Last day of trading change: {yf_func.get_last_day_percentage(df)}%')

            if risk_analysis['SHORT/LONG'] == 'LONG':
                self.short_long_label.setStyleSheet('background-color: rgb(24, 124, 41)')
                self.short_long_label.setText('Long')
                self.short_long_label.show()
            else:
                self.short_long_label.setStyleSheet('background-color: rgb(193, 44, 44)')
                self.short_long_label.setText('Short')
                self.short_long_label.show()

        except Exception as e:
            print(e)
            traceback.print_exc()

    def center(self):
        """
        Centers the Window Dialog.
        :return:
        :rtype:
        """
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        """
        Mouse Event
        :param event: mouse event
        :type event: event
        :return:
        :rtype:
        """
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        """
        Mouse Move Event
        :param event: mouse move event
        :type event: event
        :return:
        :rtype:
        """
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()


# SPLASH SCREEN
class SplashScreen(QtWidgets.QMainWindow):
    """
    Splash Screen window dialog, borderless
    """
    def __init__(self):
        """
        On initialization of Splash Screen
        """
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
