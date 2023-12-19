#!/usr/bin/env python3
from PyQt5.QtWidgets import QMainWindow, QApplication ,QLabel ,QPushButton, QAction, QProgressBar, QListWidget
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic
from mplwidget import MplWidget
from PyQt5.QtGui import QIcon
import sys
from utiles import *
import subprocess
import socket
import pystray
from PIL import Image



class ServerThread(QThread):
    progress_updated = pyqtSignal(int)
    def run(self):
        self.run = True
        # Creating The Server
        HOST = "127.0.0.1"
        PORT = 9090
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen(1)
        message = 500
        while int(message) != 100 and not self.isInterruptionRequested():
            commu, addr = server.accept()
            message = int(commu.recv(1024).decode("utf-8"))
            self.progress_updated.emit(message)
        server.close()

class BrowserThread(QThread):
    """
    This class is to open the second python file and get the internet output from it
    """
    final_value = pyqtSignal(str)
    def run(self):
        output = subprocess.check_output(['python3', PATH + 'get_data_script.py'], stderr=subprocess.STDOUT, universal_newlines=True)
        output = output.split()[0]
        self.final_value.emit(output)
    
class Every20MinuitThread(QThread):
    """
    This Thread is only used for grapping internet data evert 20 minuits
    """
    def init(self, ui):
        self.ui = ui
    def run(self):
        while True:
            print("timestart")
            time.sleep(20 * 60)
            print("timeend")

            self.ui.check_internet_method()

class TrayThread(QThread):
    """
    This class is to open the second python file and get the internet output from it
    """
    def init(self, ui):
        self.ui = ui

    def on_left_click(self):
        """
        this method show the screen of the program
        """
        self.ui.show()
        self.ui.activateWindow()

    def on_right_click(self):
        """
        this method closes the entire program
        """
        self.ui.close()

    def run(self):
        image = Image.open(PATH + "wifi.png")

        # Create a menu item with the left-click event handler
        menu = (pystray.MenuItem("show", self.on_left_click, default = True),
                pystray.MenuItem("exit", self.on_right_click))

        # Create the tray icon with the menu
        icon = pystray.Icon("tray_icon", image, "Tray Icon", menu)

        # Run the tray icon
        icon.run()


class UI(QMainWindow):
    MplWidget: MplWidget
    check_internet_button : QPushButton
    progressBar: QProgressBar
    logg_info1         : QLabel
    logg_info2         : QLabel
    when_to_stop_label : QLabel
    internet_list: QListWidget
    def __init__(self):
        super().__init__()
        uic.loadUi(PATH + "load.ui",self)
        self.setWindowIcon(QIcon(PATH + "wifi.png"))
        self.init_ui()
        self.init_data()
        
    def init_ui(self):
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.browser_thread = BrowserThread()
        self.server_thread  = ServerThread()
        self.server_thread.progress_updated.connect(self.update_progressbar)
        self.every_20_minuit_thread = Every20MinuitThread()
        self.every_20_minuit_thread.init(self)
        self.every_20_minuit_thread.start()
        self.tray_thread  = TrayThread()
        self.tray_thread.init(self)
        self.tray_thread.start()
        self.check_internet_button.clicked.connect(self.check_internet_method)
        finish = QAction("Quit", self)
        finish.triggered.connect(lambda : self.closeEvent(None))

    def init_data(self):
        self.data_file = JsonIt(PATH + "data/net.json")
        internet_data = self.data_file.read_data()
        [timestamps, values], [target_slop, target_intercepted], last_prediction, zero_date = get_params(internet_data)
        if last_prediction is None and zero_date == 0:
            self.logg_info1.setText(f"Check The internet by clicking the button above")
            self.logg_info2.setText(f"There is no enough data to predict future")
            return
        self.diffrential_data = []
        for ts, value in internet_data.items():
            target_diff = int(ts) * target_slop + target_intercepted - value
            if target_diff<0:
                self.internet_list.addItem(f"{timestamp2date(ts)}  {float(value):.2f}  {float(target_diff):.2f}")
            else:
                self.internet_list.addItem(f"{timestamp2date(ts)}  {float(value):.2f}  +{float(target_diff):.2f}")
            self.diffrential_data.append(target_diff)

        if last_prediction is None and zero_date == 1:
            self.logg_info2.setText(f"There is no enough data to predict future")
            return
        self.logg_info1.setText(f"{timestamp2date(timestamps[-1])}\n{values[-1]} GB \nRemaining")
        self.logg_info2.setText(f"It's predicted that internet will end at\n{zero_date}")
        last_row_index = self.internet_list.count() - 1
        self.internet_list.setCurrentRow(last_row_index)
        self.plot_data(timestamps, values, last_prediction, target_slop, target_intercepted)


    def check_internet_method(self):
        if not is_connected_to_internet():
            return None
        self.check_internet_button.setEnabled(False)
        self.progressBar.setValue(0)
        self.server_thread.start()
        self.browser_thread = BrowserThread()
        self.browser_thread.final_value.connect(self.update_list)
        self.browser_thread.finished.connect(self.browser_thread.deleteLater)
        self.browser_thread.start()

    def update_list(self, internet_value):
        time_now = time.time()
        self.check_internet_button.setEnabled(True)
        self.logg_info1.setText(f"{timestamp2date(time_now)}\n{internet_value} GB \nRemaining")
        data = self.data_file.read_data()
        [timestamps, values], [target_slop, target_intercepted], last_prediction, zero_date = get_params(data)
        if last_prediction is None and zero_date == 0:
            data[f"{int(time_now)}"] = float(internet_value)
            self.data_file.save_data(data)
            self.internet_list.addItem(f"{timestamp2date(time_now)}  {float(internet_value):.2f}  +0.00")
            self.logg_info2.setText(f"There is no enough data to predict future")
            return
        
        if abs(values[-1] - float(internet_value)) <0.1:
            return
        
        data[f"{int(time_now)}"] = float(internet_value)
        self.data_file.save_data(data)
        [timestamps, values], [target_slop, target_intercepted], last_prediction, zero_date = get_params(data)
        self.logg_info2.setText(f"It's predicted that internet will end at\n{zero_date}")
        self.server_thread.requestInterruption()
        target_diff = int(timestamps[-1]) * target_slop + target_intercepted - values[-1]
        if target_diff<0:
            self.internet_list.addItem(f"{timestamp2date(time_now)}  {float(internet_value):.2f}  {float(target_diff):.2f}")
        else:
            self.internet_list.addItem(f"{timestamp2date(time_now)}  {float(internet_value):.2f}  +{float(target_diff):.2f}")

        last_row_index = self.internet_list.count() - 1
        self.internet_list.setCurrentRow(last_row_index)
        self.diffrential_data.append(target_diff)
        self.plot_data(timestamps, values, last_prediction, target_slop, target_intercepted)
    
    def plot_data(self, timestamps, values, last_prediction, target_slop, target_intercepted):
        when_to_stop_time = (values[-1] - target_intercepted) / target_slop
        self.when_to_stop_label.setText(f"To set diff to zero:\n{timestamp2date(when_to_stop_time)}")
        self.MplWidget.axes1.clear()
        self.MplWidget.axes1.plot([datetime.fromtimestamp(int(ts)) for ts in timestamps]                         , values, color="r",marker='.')
        self.MplWidget.axes1.plot([datetime.fromtimestamp(timestamps[0]), datetime.fromtimestamp(timestamps[-1])], [min(QUOTA,values[0]), last_prediction],color="b")
        self.MplWidget.axes1.plot([datetime.fromtimestamp(timestamps[0]), datetime.fromtimestamp(timestamps[-1])], [min(QUOTA,values[0]), timestamps[-1] * target_slop + target_intercepted],color="g")
        self.MplWidget.axes2.plot([datetime.fromtimestamp(int(ts)) for ts in timestamps]                         , self.diffrential_data,color="#17181d")
        self.MplWidget.axes1.relim()
        self.MplWidget.axes1.autoscale_view()
        self.MplWidget.axes2.relim()
        self.MplWidget.axes2.autoscale_view()
        self.MplWidget.canvas.draw_idle()

    def update_progressbar(self, value):
        self.progressBar.setValue(value)
    
    def closeEvent(self, event):
        self.tabWidget.setCurrentIndex(0)
        if event.spontaneous():
            self.hide()
            event.ignore()
        else:
            event.accept()

app = QApplication(sys.argv)
wind = UI()
app.exec_()

