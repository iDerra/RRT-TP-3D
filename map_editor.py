from PyQt5.QtWidgets import (QApplication, QWidget, QFormLayout, QLineEdit,
                            QPushButton, QMessageBox, QDialog, QListWidget, 
                            QListWidgetItem, QDockWidget, QMenu, QAction, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import sys
import json 
import os 

from environment import Environment, EnvSettings
from mapEditor.startButton import StartPointDialog
from mapEditor.goalButton import GoalPointDialog
from mapEditor.obstacleButton import ObstacleDialog

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
        self.environment = None

    def create_environment(self):
        """
        Creates the Environment instance based on user input.
        Handles errors gracefully.
        """
        try:
            size = []
            for line_edit in self.size_inputs:
                text = line_edit.text().strip()
                if not text:
                    raise ValueError("All size fields must be filled.")

                min_val_str, max_val_str = text.split(",")
                min_val = float(min_val_str.strip())
                max_val = float(max_val_str.strip())

                if min_val >= max_val:
                    raise ValueError("Minimum value must be less than maximum value.")
                size.append((min_val, max_val))

            obs = []
            start = None
            goal = None
            settings = EnvSettings()
            self.environment = Environment(size, obs, start, goal, settings)

            # --- Sidebar ---
            self.add_obstacle_sidebar()

            # --- Buttons ---
            self.add_start_button()
            self.add_goal_button()
            self.add_obstacle_button()
            self.add_save_button()

            self.environment.show()
            self.close()

        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", "An unexpected error occurred:\n" + str(e))

    def add_start_button(self):
        """Adds the 'Add Start Point' button to the Environment window."""
        start_button = QPushButton("Add Start Point")
        start_button.clicked.connect(self.get_start_point)

        central_widget = self.environment.centralWidget()
        if central_widget:
            layout = central_widget.layout()
            if layout:
                layout.addWidget(start_button)
            else:
                print("Error: No layout found in central widget.")
        else:
            print("Error: No central widget found.")

    def add_obstacle_sidebar(self):
        """Adds a sidebar to display the list of obstacles."""

        self.obstacle_list_widget = QListWidget()
        self.obstacle_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.obstacle_list_widget.customContextMenuRequested.connect(self.show_obstacle_context_menu)
        dock_widget = QDockWidget("Obstacles", self.environment)
        dock_widget.setWidget(self.obstacle_list_widget)
        self.environment.addDockWidget(Qt.RightDockWidgetArea, dock_widget)
        dock_widget.setMinimumWidth(200)

    def show_obstacle_context_menu(self, position):
        """
        Shows the context menu for the obstacle list.

        Args:
            position (QPoint): The position of the right-click.
        """

        item = self.obstacle_list_widget.itemAt(position)
        if item is None:
            return

        obstacle_data = item.data(Qt.UserRole)
        menu = QMenu(self) 

        edit_action = QAction("Edit Obstacle", self)
        delete_action = QAction("Delete", self)

        edit_action.triggered.connect(lambda: self.edit_obstacle(obstacle_data))
        delete_action.triggered.connect(lambda: self.delete_obstacle(obstacle_data))

        menu.addAction(edit_action)
        menu.addAction(delete_action)

        menu.exec_(self.obstacle_list_widget.mapToGlobal(position))

    def edit_obstacle(self, obstacle_data):
        """
        Edits the selected obstacle.
        """
        dialog = ObstacleDialog(obstacle_data=obstacle_data)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            try:
                obstacle_id, pos, size, color = dialog.get_obstacle_data()

                if not (self.environment.size[0][0] <= pos[0] <= self.environment.size[0][1] and
                        self.environment.size[1][0] <= pos[1] <= self.environment.size[1][1] and
                        self.environment.size[2][0] <= pos[2] <= self.environment.size[2][1]):
                    QMessageBox.warning(self.environment, "Out of Bounds", "Obstacle position is outside the environment bounds.")
                    return

                if any(s <= 0 for s in size):
                    QMessageBox.warning(self.environment, "Invalid Size", "Obstacle size must be positive.")
                    return
                
                for i, data in enumerate(self.environment.obstacles):
                    if data[0] == obstacle_id:
                        self.environment.obstacles[i] = [obstacle_id, pos, size, color]
                        break

                self.environment.updateView()
                self.update_obstacle_list()


            except ValueError as e:
                QMessageBox.critical(self.environment, "Error", str(e))

    def delete_obstacle(self, obstacle_data):
        """
        Deletes the selected obstacle.
        """
        obstacle_id = obstacle_data[0]

        index_to_remove = -1
        for i, data in enumerate(self.environment.obstacles):
            if data[0] == obstacle_id:
                index_to_remove = i
                break

        if index_to_remove != -1:
            del self.environment.obstacles[index_to_remove]

            for i in range(self.obstacle_list_widget.count()):
                item = self.obstacle_list_widget.item(i)
                if item.data(Qt.UserRole)[0] == obstacle_id:
                    self.obstacle_list_widget.takeItem(i)
                    break

            self.environment.updateView()
            self.update_obstacle_list()
            
    def add_goal_button(self):
        """Adds the 'Add Goal Point' button to the Environment window."""
        goal_button = QPushButton("Add Goal Point")
        goal_button.clicked.connect(self.get_goal_point)

        central_widget = self.environment.centralWidget()
        if central_widget:
            layout = central_widget.layout()
            if layout:
                layout.addWidget(goal_button)
            else:
                print("Error: No layout found in central widget.")
        else:
            print("Error: No central widget found.")

    def add_obstacle_button(self):
        """Adds the 'Add Obstacle' button to the Environment window."""
        obstacle_button = QPushButton("Add Obstacle")
        obstacle_button.clicked.connect(self.get_obstacle_data)

        central_widget = self.environment.centralWidget()
        if central_widget:
            layout = central_widget.layout()
            if layout:
                layout.addWidget(obstacle_button)
            else:
                print("Error: No layout found in central widget.")
        else:
            print("Error: No central widget found.")
    
    def get_start_point(self):
        """Gets the start point coordinates from the user and sets them."""
        dialog = StartPointDialog(self.environment.size)
        result = dialog.exec_() 
        if result == QDialog.Accepted:
            try:
                x, y, z = dialog.get_coordinates()
                if not (self.environment.size[0][0] <= x <= self.environment.size[0][1] and
                        self.environment.size[1][0] <= y <= self.environment.size[1][1] and
                        self.environment.size[2][0] <= z <= self.environment.size[2][1]):
                    QMessageBox.warning(self.environment, "Out of Bounds", "Start point coordinates are outside the environment bounds.")
                    return 

                self.environment.start = (x, y, z)
                self.environment.updateView()

            except ValueError as e:
                QMessageBox.critical(self.environment, "Error", str(e))

    def get_goal_point(self):
        """Gets the goal point coordinates from the user and sets them."""
        dialog = GoalPointDialog(self.environment.size)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            try:
                x, y, z = dialog.get_coordinates()
                if not (self.environment.size[0][0] <= x <= self.environment.size[0][1] and
                        self.environment.size[1][0] <= y <= self.environment.size[1][1] and
                        self.environment.size[2][0] <= z <= self.environment.size[2][1]):
                    QMessageBox.warning(self.environment, "Out of Bounds", "Goal point coordinates are outside the environment bounds.")
                    return

                self.environment.goal = (x, y, z)
                self.environment.updateView()

            except ValueError as e:
                QMessageBox.critical(self.environment, "Error", str(e))

    def get_obstacle_data(self):
        """Gets obstacle data from the user and adds the obstacle to the environment."""
        dialog = ObstacleDialog(self.next_obstacle_id)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            try:
                obstacle_id, pos, size, color = dialog.get_obstacle_data()

                if not (self.environment.size[0][0] <= pos[0] <= self.environment.size[0][1] and
                        self.environment.size[1][0] <= pos[1] <= self.environment.size[1][1] and
                        self.environment.size[2][0] <= pos[2] <= self.environment.size[2][1]):
                    QMessageBox.warning(self.environment, "Out of Bounds", "Obstacle position is outside the environment bounds.")
                    return

                if any(s <= 0 for s in size):
                    QMessageBox.warning(self.environment, "Invalid Size", "Obstacle size must be positive.")
                    return

                self.environment.obstacles.append([obstacle_id, pos, size, color])
                self.next_obstacle_id += 1
                self.environment.updateView()
                self.update_obstacle_list()

            except ValueError as e:
                QMessageBox.critical(self.environment, "Error", str(e))

    def update_obstacle_list(self):
        """Updates the obstacle list in the sidebar."""

        self.obstacle_list_widget.clear()
        for obstacle_data in self.environment.obstacles:
            obstacle_id, pos, size, color = obstacle_data
            item_text = f"ID: {obstacle_id}, Pos: {pos}, Color: {color}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, obstacle_data)

            item.setBackground(QColor(*[int(c * 255) for c in color]))
            self.obstacle_list_widget.addItem(item)

    def add_save_button(self):
        """Adds a 'Save Map' button to the Environment window."""
        save_button = QPushButton("Save Map")
        save_button.clicked.connect(self.save_map)

        central_widget = self.environment.centralWidget()
        if central_widget:
            layout = central_widget.layout()
            if layout:
                layout.addWidget(save_button)
            else:
                print("Error: No layout found in central widget.")
        else:
            print("Error: No central widget found.")

    def save_map(self):
        """Saves the current map configuration to a file."""

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Map", "./maps/", "JSON Files (*.json)", options=options)

        if file_name:
            if not file_name.endswith(".json"):
                file_name += ".json"

            map_data = {
                "mapSize": self.environment.size,
                "posStart": self.environment.start,
                "posGoal": self.environment.goal,
                "listObstacles": self.environment.obstacles,
            }

            try:
                os.makedirs("./maps", exist_ok=True)

                with open(file_name, 'w') as f:
                    json.dump(map_data, f, indent=4)

                QMessageBox.information(self, "Map Saved", f"Map saved to {file_name}")

            except Exception as e:
                QMessageBox.critical(self, "Error Saving Map", str(e))

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
