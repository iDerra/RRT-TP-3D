from PyQt5.QtWidgets import (QWidget, QFormLayout, QLineEdit, QPushButton, QMessageBox)
from environment import Environment, EnvSettings
from mapEditor.buttonManager import ButtonManager

class SizeInputDialog(QWidget):
    """
    A dialog window to get the environment size from the user.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Set Environment Size")
        self.size_inputs = []
        self.next_obstacle_id = 1  
        self.initUI()
        self.environment = None
        

    def initUI(self):
        layout = QFormLayout()

        for axis in ["X (min,max)", "Y (min,max)", "Z (min,max)"]:
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(axis)
            layout.addRow(axis + ":", line_edit)
            self.size_inputs.append(line_edit)

        submit_button = QPushButton("Create Environment")
        submit_button.clicked.connect(self.create_environment)
        layout.addRow(submit_button)

        self.setLayout(layout)


    def create_environment(self):
        """
        Creates the Environment instance based on user input.
        Handles errors gracefully.
        """
        try:
            size = self.get_size_input()

            obs = []
            start = None
            goal = None
            settings = EnvSettings()

            self.environment = Environment(size, obs, start, goal, settings)
            self.button_manager = ButtonManager(self.environment, self)
            self.button_manager.add_buttons()

            self.environment.show()
            self.close()

        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{e}")


    def get_size_input(self):
        """Gets and validates the size input from the user."""
        size = []
        for line_edit in self.size_inputs:
            text = line_edit.text().strip()
            if not text:
                raise ValueError("All size fields must be filled.")

            try:
                min_val_str, max_val_str = text.split(",")
                min_val = float(min_val_str.strip())
                max_val = float(max_val_str.strip())
            except ValueError:
                raise ValueError("Invalid size format. Use numbers separated by commas.")

            if min_val >= max_val:
                raise ValueError("Minimum value must be less than maximum value.")
            size.append((min_val, max_val))
        return size