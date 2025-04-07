import sys
from PyQt5.QtWidgets import QApplication
from gesture_app import GestureApp

def main():
    app = QApplication(sys.argv)
    window = GestureApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 