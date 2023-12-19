from PyQt5.QtWidgets import QMainWindow, QApplication ,QLabel ,QPushButton, QAction, QProgressBar, QListWidget, QDialog, QListWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os
from utiles import *
class GraphEdit(QDialog):
    all_data_list:      QListWidget
    selected_data_list: QListWidget
    add_button    : QPushButton
    remove_button : QPushButton
    def __init__(self):
        super().__init__()
        loadUi(PATH + "graph_edit.ui", self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Graph Edit")
        self.setWindowIcon(QIcon(PATH + "wifi.png"))
        self.show()
        self.data = []
        self.load_old_data()
        self.all_data_list.itemClicked.connect(self.add_to_graphs)
    def load_old_data(self):
        for item in os.listdir("data"):
            if item.endswith(".json"):
                item = item[:-5]
            if "-" in item:
                start_time, end_time = item.split("-")
                self.all_data_list.addItem(timestamp2date(start_time) + " " + timestamp2date(end_time))
                self.data.append(timestamp2date(start_time) + " " + timestamp2date(end_time))

    def add_to_graphs(self, item):
        item: QListWidgetItem
        # print(self.data.index(item.text()))
        print(self.all_data_list.selectedItems())

if __name__ == "__main__":
    app = QApplication([])
    graph_edit = GraphEdit()
    app.exec_()    