from PyQt5.QtWidgets import QApplication
import sys
from mapEditor.sizeInput import SizeInputDialog


def create_and_show_environment():
    """
    Creates and shows the environment after getting the size from the user.
    """
    app = QApplication(sys.argv)
    input_dialog = SizeInputDialog()
    input_dialog.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    create_and_show_environment()