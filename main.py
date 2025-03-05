from environment import Environment, EnvSettings
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QWidget
import sys
import json

from mainInterface.mainDialog import EnvironmentWindow

# Coordinate System Convention:
# X: Horizontal (Left/Right)
# Y: Depth (Front/Back)
# Z: Vertical (Up/Down)

"""
    How to use:
        - Define the size, obstacles, start and goal.
        - Create the environment, you can modify the settings as you wish using the EnvSettings class.
        - Define the RRTSettings, don't modify them if you don't know what you are doing.
        - Get the trajectory waypoints by calling the search function.
        - Plot the trajectory

    Important! Do not create start and goal nodes inside an obstacle or outside the size of the map.
"""


class MapLoader(QWidget):  
    def __init__(self):
        super().__init__()
        self.map_data = None
        self.load_map()

    def load_map(self):
        """Loads a map from a JSON file."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load Map", "./maps/", "JSON Files (*.json)", options=options
        )

        if file_name:
            try:
                with open(file_name, 'r') as f:
                    self.map_data = json.load(f)
            except Exception as e:
                QMessageBox.critical(self, "Error Loading Map", str(e))
                
                sys.exit(1)

    def get_map_data(self):
        """Returns the loaded map data."""
        return self.map_data



if __name__ == '__main__':
    app = QApplication(sys.argv)

    # --- Load Map ---
    map_loader = MapLoader()
    map_data = map_loader.get_map_data()

    if map_data is None:
        sys.exit(0)

    # --- Extract Map Data ---
    size = map_data["mapSize"]
    start = map_data["posStart"]
    goal = map_data["posGoal"]
    obs = map_data["listObstacles"]

    # --- Create Environment ---
    env_settings = EnvSettings()
    env = EnvironmentWindow(size, obs, start, goal, env_settings)

    # --- Show Environment ---
    env.show()
    sys.exit(app.exec_())