#!/usr/bin/env python3
from PyQt5.QtWidgets import QMainWindow, QApplication ,QLabel ,QPushButton, QAction, QProgressBar, QListWidget
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5 import uic
from mplwidget import MplWidget
from PyQt5.QtGui import QIcon
import sys
from utiles import *
from get_data_api import *
import pystray
from PIL import Image

class ApiCallingThread(QThread):
    """This class is responsible for calling the api with the user data and get the remaining GB from mywe site"""
    final_value = pyqtSignal(float)
    no_internet = pyqtSignal()
    def run(self):
        timer = QTimer()
        timer.setInterval(60 * 1000)
        timer.timeout.connect(self.no_internet.emit)
        timer.start()
        if not is_connected_to_internet():
            self.no_internet.emit()
            timer.stop()
            return None
        remaining = get_user_data()
        if remaining is None:
            timer.stop()
            self.no_internet.emit() # error in the connection
        else:
            timer.stop()
            self.final_value.emit(remaining)

class TrayThread(QThread):
    """This class is only for handeling the thread of the tray"""
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
        self.api_calling_thread = ApiCallingThread()
        self.api_calling_thread.final_value.connect(self.update_list)
        self.api_calling_thread.no_internet.connect(lambda: self.check_internet_button.setEnabled(True))
        self.timer = QTimer()
        self.timer.setInterval(10 * 60000)
        self.timer.timeout.connect(self.get_user_data)
        self.timer.start()
        self.tray_thread  = TrayThread()
        self.tray_thread.init(self)
        self.tray_thread.start()
        self.check_internet_button.clicked.connect(self.get_user_data)
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


    def get_user_data(self):
        self.check_internet_button.setEnabled(False)
        self.api_calling_thread.start()

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
        
        if abs(values[-1] - float(internet_value)) <0.01:
            return
        
        elif abs(values[-1] - float(internet_value)) > 130:
            os.rename(PATH + "data/net.json", PATH + f"data/{timestamps[0]}-{timestamps[-1]}.json")
            with open(PATH + "data/net.json", 'w') as f:
                json.dump({}, f)
            data = self.data_file.read_data()
            
        data[f"{int(time_now)}"] = float(internet_value)
        self.data_file.save_data(data)
        [timestamps, values], [target_slop, target_intercepted], last_prediction, zero_date = get_params(data)
        self.logg_info2.setText(f"It's predicted that internet will end at\n{zero_date}")
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

