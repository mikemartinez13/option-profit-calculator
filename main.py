from PyQt5 import QtWidgets as qtw
import src.window as win
import sys
import argparse

def main(demo: bool = False):
    app = qtw.QApplication([])
    window = win.MainWindow(demo=demo)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Option Profit Calculator Configs')
    parser.add_argument('-d', '--demo', action='store_true',
                        help='Run demo version of the app for users who do not have an active Schwab Developer account.')

    args = parser.parse_args()

    main(args.demo)