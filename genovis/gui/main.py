import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from .genovis_gui import Ui_GENOVIS_GUI
class MainWindow(QMainWindow, Ui_GENOVIS_GUI):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
def main():
    os.environ["GENOVIS_GUI"] = "1"
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()