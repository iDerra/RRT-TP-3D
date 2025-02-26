from PyQt5.QtWidgets import (QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QLabel, QDialog)

class GoalPointDialog(QDialog):
    """
    Dialog for getting the goal point coordinates.
    """
    def __init__(self, env_size):
        super().__init__()
        self.setWindowTitle("Set Goal Point") 
        self.env_size = env_size
        self.x_input = QLineEdit()
        self.y_input = QLineEdit()
        self.z_input = QLineEdit()
        self.initUI()

    def initUI(self):
        layout = QFormLayout()

        size_label = QLabel(f"Environment Size: X=({self.env_size[0][0]}, {self.env_size[0][1]}), Y=({self.env_size[1][0]}, {self.env_size[1][1]}), Z=({self.env_size[2][0]}, {self.env_size[2][1]})")
        layout.addRow(size_label)

        self.x_input.setPlaceholderText("X")
        self.y_input.setPlaceholderText("Y")
        self.z_input.setPlaceholderText("Z")

        layout.addRow("X:", self.x_input)
        layout.addRow("Y:", self.y_input)
        layout.addRow("Z:", self.z_input)

        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addRow(button_box)

        self.setLayout(layout)

    def get_coordinates(self):
        """
        Returns the coordinates entered by the user as floats.
        Raises ValueError if the input is invalid.
        """
        x_str = self.x_input.text().strip()
        y_str = self.y_input.text().strip()
        z_str = self.z_input.text().strip()

        if not x_str or not y_str or not z_str:
            raise ValueError("All coordinates must be provided.")

        try:
            x = float(x_str)
            y = float(y_str)
            z = float(z_str)
        except ValueError:
            raise ValueError("Invalid coordinate format.  Use numbers.")

        return x, y, z