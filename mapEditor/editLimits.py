from PyQt5.QtWidgets import (QFormLayout, QLineEdit, QPushButton, QDialog)

class EditLimitsDialog(QDialog):
    """
    Dialog for editing the environment size (map limits).
    """
    def __init__(self, current_size):
        super().__init__()
        self.setWindowTitle("Edit Map Limits")
        self.size_inputs = []
        self.current_size = current_size
        self.initUI()

    def initUI(self):
        layout = QFormLayout()

        for axis, (min_val, max_val) in zip(["X", "Y", "Z"], self.current_size):
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"{axis} (min,max)")
            line_edit.setText(f"{min_val}, {max_val}") 
            layout.addRow(f"{axis} (min,max):", line_edit)
            self.size_inputs.append(line_edit)

        button_box = QFormLayout()
        submit_button = QPushButton("Update Limits")
        cancel_button = QPushButton("Cancel")
        submit_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_box.addRow(submit_button, cancel_button)
        layout.addRow(button_box)

        self.setLayout(layout)

    def get_new_size(self):
        """Gets and validates the new size input from the user."""
        new_size = []
        try:
            for line_edit in self.size_inputs:
                text = line_edit.text().strip()
                if not text:
                    raise ValueError("All size fields must be filled.")

                min_val_str, max_val_str = text.split(",")
                min_val = float(min_val_str.strip())
                max_val = float(max_val_str.strip())

                if min_val >= max_val:
                    raise ValueError("Minimum value must be less than maximum value.")
                new_size.append((min_val, max_val))
        except ValueError as e:
            raise ValueError("Invalid size format. " + str(e))

        return new_size