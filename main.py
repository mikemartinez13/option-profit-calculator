from PyQt5 import QtWidgets as qtw
import src.window as win
import sys

app = qtw.QApplication([])
window = win.MainWindow()
window.show()
sys.exit(app.exec_())