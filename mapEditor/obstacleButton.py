from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QLabel, QColorDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class ObstacleDialog(QDialog):
    """
    Dialog for getting obstacle properties (position, size, color).
    """
    def __init__(self, env_size, next_obstacle_id=None, obstacle_data=None):
        super().__init__()

        self.is_editing = obstacle_data is not None
        self.env_size = env_size

        if self.is_editing:
            self.setWindowTitle("Edit Obstacle")
            self.obstacle_id, self.pos, self.size, self.color = obstacle_data
        else:
            self.setWindowTitle("Add Obstacle")
            self.obstacle_id = next_obstacle_id
            self.pos = [0.0, 0.0, 0.0] 
            self.size = [1.0, 1.0, 1.0]
            self.color = (1, 0, 0, 1)

        self.pos_inputs = []
        self.size_inputs = []
        self.initUI()

    def initUI(self):
        layout = QFormLayout()

        size_label = QLabel(f"Environment Size: X=({self.env_size[0][0]}, {self.env_size[0][1]}), Y=({self.env_size[1][0]}, {self.env_size[1][1]}), Z=({self.env_size[2][0]}, {self.env_size[2][1]})")
        layout.addRow(size_label)

        id_label = QLabel(f"Obstacle ID: {self.obstacle_id}")
        layout.addRow(id_label)

        for axis, current_pos in zip(["X", "Y", "Z"], self.pos):
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Position {axis}")
            line_edit.setText(str(current_pos))
            layout.addRow(f"Position {axis}:", line_edit)
            self.pos_inputs.append(line_edit)

        for axis, current_size in zip(["X", "Y", "Z"], self.size):
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Size {axis}")
            line_edit.setText(str(current_size))
            layout.addRow(f"Size {axis}:", line_edit)
            self.size_inputs.append(line_edit)

        self.color_button = QPushButton("Pick Color")
        self.color_button.clicked.connect(self.pick_color)
        self.update_color_button()
        layout.addRow(self.color_button)

        button_box = QHBoxLayout()
        if self.is_editing:
            ok_button = QPushButton("Save Changes")
        else:
            ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addRow(button_box)

        self.setLayout(layout)

    def pick_color(self):
        """Opens a color dialog and updates the selected color."""
        color = QColorDialog.getColor(QColor(*[int(c*255) for c in self.color]))
        if color.isValid():
            self.color = (color.redF(), color.greenF(), color.blueF(), color.alphaF())
            self.update_color_button()

    def update_color_button(self):
        """Updates the color of the color button."""
        rgba_color = [int(c * 255) for c in self.color]
        self.color_button.setStyleSheet(f"background-color: rgba({rgba_color[0]}, {rgba_color[1]}, {rgba_color[2]}, {rgba_color[3]});")

    def get_obstacle_data(self):
        """
        Gets the obstacle data (ID, position, size, color) from the inputs.
        Raises ValueError if the input is invalid.
        """
        try:
            pos = [float(input_field.text().strip()) for input_field in self.pos_inputs]
            size = [float(input_field.text().strip()) for input_field in self.size_inputs]

            if len(pos) != 3 or len(size) != 3:
                raise ValueError("All position and size fields must be filled.")
            return self.obstacle_id, pos, size, self.color

        except ValueError:
            raise ValueError("Invalid input.  Use numbers for position and size.")