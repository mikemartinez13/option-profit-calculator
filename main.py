from PyQt5 import QtWidgets as qtw
import src.window as win
import sys
import argparse

def main(demo: bool = False):
    app = qtw.QApplication([])
    app.setStyleSheet('''
                    QWidget { 
                    font-family: Roboto;
                    font-size: 14px;
                    color: white;
                    /* background: #1A273C; */
                    background: #17212e;
                    }

                    QPushButton {
                    /* background-color: #614393; */
                    background-color: #2c405a;
                    padding: 8px;
                    border-radius: 5px 5px 0 0;
                    }

                    QPushButton:hover {
                    background-color: #8e64d4;
                    }
                    
                    ''')
    window = win.MainWindow(demo=demo)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Option Profit Calculator Configs')
    parser.add_argument('-d', '--demo', action='store_true',
                        help='Run demo version of the app for users who do not have an active Schwab Developer account.')

    args = parser.parse_args()

    main(args.demo)