from environment import Environment, EnvSettings
from rrt import RRTSettings, search
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QWidget, QPushButton
import sys
import json

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
    In the search function you can use the nTests parameter to run x tests without visualisation, to test the performance of the algorithm.
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


class EnvironmentWindow(Environment):
    """
    Extends the Environment class to include a button for running RRT.
    """
    def __init__(self, size, obs, start, goal, settings):
        super().__init__(size, obs, start, goal, settings) 
        self.rrt_settings = RRTSettings()
        self.add_rrt_button()


    def add_rrt_button(self):
        """Adds a 'Run RRT' button to the Environment window."""
        rrt_button = QPushButton("Run RRT")
        rrt_button.clicked.connect(self.run_rrt)

        central_widget = self.centralWidget()
        if central_widget:
            layout = central_widget.layout()
            if layout:
                layout.addWidget(rrt_button)
            else:
                print("Error: No layout found in central widget.")
        else:
            print("Error: No central widget found.")

    def run_rrt(self):
        """Executes the RRT search and plots the trajectory."""
        if self.start is None or self.goal is None:
            QMessageBox.warning(self, "Start/Goal Not Set", "Please set both start and goal points before running RRT.")
            return

        waypoints = search(self.size, self.start, self.goal, self.obstacles, self.rrt_settings, nTests=0)
        self.plotTrajectory(waypoints)


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