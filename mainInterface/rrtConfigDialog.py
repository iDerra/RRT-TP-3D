from PyQt5.QtWidgets import QCheckBox, QMessageBox, QPushButton, QLineEdit, QDialog, QFormLayout, QLabel
from rrt import RRTSettings

class RRTConfigDialog(QDialog):
    """
    A dialog window for configuring RRT algorithm settings.

    :param settings: The initial RRT settings to be displayed.
    """
    def __init__(self, settings):
        super().__init__()
        self.setWindowTitle("RRT Configuration")

        self.safeDistance = QLineEdit(str(settings.safeDistance))
        self.goalDistance = QLineEdit(str(settings.goalDistance))
        self.nodeDistance = QLineEdit(str(settings.nodeDistance))
        self.nodeLimit = QLineEdit(str(settings.nodeLimit))
        self.numQuadrantsPerAxis = QLineEdit(str(settings.numQuadrantsPerAxis))
        self.quadrantProb = QLineEdit(str(settings.quadrantProb))

        self.layout = QFormLayout()
        self.layout.addRow("Safety distance to obstacles:", self.safeDistance)
        self.layout.addRow("Minimum distance to goal:", self.goalDistance)
        self.layout.addRow("Distance between nodes:", self.nodeDistance)
        self.layout.addRow("Maximum number of expanded nodes:", self.nodeLimit)

        self.quadrants_check = QCheckBox("Use quadrants?")
        self.quadrants_check.setChecked(settings.quadrants)
        self.quadrants_check.stateChanged.connect(self.toggle_quadrant_fields)

        self.layout.addRow(self.quadrants_check)

        self.numQuadrantsPerAxis_label = QLabel("Number of Quadrants Per Axis:")
        self.quadrantProb_label = QLabel("Quadrant Probability:")
        self.layout.addRow(self.numQuadrantsPerAxis_label, self.numQuadrantsPerAxis)
        self.layout.addRow(self.quadrantProb_label, self.quadrantProb)
        self.numQuadrantsPerAxis_label.setVisible(False)
        self.numQuadrantsPerAxis.setVisible(False)
        self.quadrantProb_label.setVisible(False)
        self.quadrantProb.setVisible(False)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        self.layout.addRow(ok_button, cancel_button)
        self.setLayout(self.layout) 

        self.toggle_quadrant_fields(self.quadrants_check.isChecked())


    def toggle_quadrant_fields(self, state):
        """
        Shows or hides the quadrant-related input fields.
        
        :param state: The state of the checkbox (Qt.Checked = 2, Qt.Unchecked = 0).
        """
        
        visible = state == 2 
        self.numQuadrantsPerAxis_label.setVisible(visible)
        self.numQuadrantsPerAxis.setVisible(visible)
        self.quadrantProb_label.setVisible(visible)
        self.quadrantProb.setVisible(visible)

    def get_settings(self):
        """
        Retrieves the RRT settings from the input fields and returns them as an RRTSettings object.

        :return: An RRTSettings object containing the configured settings, or a default RRTSettings object if there was an error.
        """
        try:
            settings = RRTSettings()
            settings.safeDistance = float(self.safeDistance.text())
            settings.goalDistance = float(self.goalDistance.text())
            settings.nodeDistance = float(self.nodeDistance.text())
            settings.nodeLimit = int(self.nodeLimit.text())
            settings.quadrants = self.quadrants_check.isChecked()

            if settings.quadrants:
                settings.numQuadrantsPerAxis = int(self.numQuadrantsPerAxis.text())
                settings.quadrantProb = float(self.quadrantProb.text())
            else:
                settings.numQuadrantsPerAxis = 2
                settings.quadrantProb = 0.5

            return settings
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid input values.")
            return RRTSettings()