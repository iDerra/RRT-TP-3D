from PyQt5.QtWidgets import QPushButton, QLineEdit, QCheckBox, QDialog, QFormLayout
from .rrtConfigDialog import RRTConfigDialog

class MultiTestDialog(QDialog):
    """
    A dialog window for configuring and initiating multiple RRT tests.

    :param rrt_settings: Initial RRT settings to use.
    """
    def __init__(self, rrt_settings):
        super().__init__()
        self.setWindowTitle("Multi-Test Configuration")

        self.num_tests_input = QLineEdit()
        self.num_tests_input.setText("1")

        self.configure_rrt_button = QPushButton("Configure RRT Settings")
        self.configure_rrt_button.clicked.connect(self.configure_rrt)

        self.visualization_check = QCheckBox("Enable Visualization")
        self.visualization_check.setChecked(True)

        self.start_tests_button = QPushButton("Start Tests")
        self.start_tests_button.clicked.connect(self.accept)


        layout = QFormLayout()
        layout.addRow("Number of Tests:", self.num_tests_input)
        layout.addRow(self.configure_rrt_button)
        layout.addRow("Visualization:", self.visualization_check)
        layout.addRow(self.start_tests_button)

        self.setLayout(layout)
        self.rrt_settings = rrt_settings

    def configure_rrt(self):
        """
        Opens the RRT configuration dialog (RRTConfigDialog) to allow the user to modify RRT settings.
        """
        rrt_config_dialog = RRTConfigDialog(self.rrt_settings)
        if rrt_config_dialog.exec_():
            self.rrt_settings = rrt_config_dialog.get_settings()
        
    def get_num_tests(self):
        """
        Gets the number of tests to run, as entered by the user.

        :return: The number of tests.
        """
        try:
            return int(self.num_tests_input.text())
        except ValueError:
            return 1

    def get_visualization(self):
        """
        Gets the visualization setting (enabled or disabled).

        :return: True if visualization is enabled, False otherwise.
        """
        return self.visualization_check.isChecked()
    
    def get_rrt_settings(self):
        """
        Gets the current RRT settings.

        :return: The RRT settings.
        """
        return self.rrt_settings