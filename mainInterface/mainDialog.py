from environment import Environment
from rrt import RRTSettings, search
from PyQt5.QtWidgets import QMessageBox, QPushButton, QApplication, QHBoxLayout
from .multiTestDialog import MultiTestDialog
from .rrtConfigDialog import RRTConfigDialog
import time

class EnvironmentWindow(Environment):
    """
    Extends the Environment class to include buttons for running RRT and configuring settings.

    :param size: The dimensions of the environment (width, length, height).
    :param obs: A list of obstacles.
    :param start: The starting position (x, y, z).
    :param goal: The goal position (x, y, z).
    :param settings: An object containing environment display settings.
    :type settings: `EnvSettings`
    """
    def __init__(self, size, obs, start, goal, settings):
        super().__init__(size, obs, start, goal, settings)
        self.rrt_settings = RRTSettings()
        self.add_buttons()


    def add_buttons(self):
        """Adds 'Run RRT', 'Configure RRT', and 'Multi-Test' buttons."""
        rrt_button = QPushButton("Run RRT")
        rrt_button.clicked.connect(self.run_rrt)

        config_rrt_button = QPushButton("Configure RRT")
        config_rrt_button.clicked.connect(self.configure_rrt)

        multi_test_button = QPushButton("Multi-Test")
        multi_test_button.clicked.connect(self.run_multi_test)

        central_widget = self.centralWidget()
        if central_widget:
            layout = central_widget.layout()
            if layout:
                button_layout = QHBoxLayout()
                button_layout.addWidget(rrt_button)
                button_layout.addWidget(config_rrt_button)
                button_layout.addWidget(multi_test_button)
                layout.addLayout(button_layout)
            else:
                print("Error: No layout found in central widget.")
        else:
            print("Error: No central widget found.")

    def configure_rrt(self):
        """Opens a dialog to configure RRT settings."""
        config_dialog = RRTConfigDialog(self.rrt_settings)
        if config_dialog.exec_():
            self.rrt_settings = config_dialog.get_settings()


    def run_rrt(self):
        """Executes the RRT search and plots the trajectory."""
        if self.start is None or self.goal is None:
            QMessageBox.warning(self, "Start/Goal Not Set", "Please set both start and goal points before running RRT.")
            return

        waypoints = search(self.size, self.start, self.goal, self.obstacles, self.rrt_settings)
        if waypoints is not None:
            self.clear_scene()
            self.plotTrajectory(waypoints)
            self.update()


    def run_multi_test(self):
        """Opens a dialog to configure and run multiple RRT tests."""

        def run_test(i, num_tests, visualization):
            """
            Inner function to run a single test.
            
            :param i: actual index.
            :param num_tests: number of test to do.
            :param visualization: boolean to plot the trajectory.
            """
            file = open("multi-testLog.log", "a")
            try:
                if visualization:
                    waypoints = search(self.size, self.start, self.goal, self.obstacles, self.rrt_settings)
                    if waypoints is not None:
                        self.plotTrajectory(waypoints)
                        self.update()
                        QApplication.processEvents()
                else:
                    waypoints = search(self.size, self.start, self.goal, self.obstacles, self.rrt_settings)

                if waypoints is not None:
                    print(f"{i + 1}/{num_tests}")
                    file.write(f"{i + 1}/{num_tests} - Nodes: " + str(len(waypoints)) + "\n")
                else:
                    print(f"{i + 1}/{num_tests} - No path found")
                    file.write(f"{i + 1}/{num_tests} - No path found\n")
            except Exception as e:
                print(f"Error during test {i+1}: {e}")
                file.write(f"Error during test {i+1}: {str(e)}\n")

            finally:
                file.close()

        dialog = MultiTestDialog(self.rrt_settings)
        if dialog.exec_():
            num_tests = dialog.get_num_tests()
            visualization = dialog.get_visualization()
            self.rrt_settings = dialog.get_rrt_settings()

            if self.start is None or self.goal is None:
                QMessageBox.warning(self, "Start/Goal Not Set", "Please set both start and goal points before running RRT.")
                return

            file = open("multi-testLog.log", "a")
            file.write("\n--- New Test ---\n")
            file.write("- RRT Settings -\n")
            file.write(f"safeDistance: {self.rrt_settings.safeDistance} | goalDistance: {self.rrt_settings.goalDistance} | nodeDistance: {self.rrt_settings.nodeDistance} | nodeLimit: {self.rrt_settings.nodeLimit} | quadrants: {self.rrt_settings.quadrants} | numQuadrantsPerAxis: {self.rrt_settings.numQuadrantsPerAxis} | quadrantProb: {self.rrt_settings.quadrantProb}\n")
            file.close()
            for i in range(num_tests):
                self.clear_scene()
                run_test(i, num_tests, visualization)
                time.sleep(0.5)