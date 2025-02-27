from PyQt5.QtWidgets import QPushButton, QMessageBox, QDialog
from mapEditor.startButton import StartPointDialog
from mapEditor.goalButton import GoalPointDialog
from mapEditor.obstacleButton import ObstacleDialog
from mapEditor.obstacleSidebar import ObstacleSidebar
from mapEditor.mapSaver import MapSaver
from mapEditor.editLimits import EditLimitsDialog

class ButtonManager:
    def __init__(self, environment, size_input_dialog):
        self.environment = environment
        self.size_input_dialog = size_input_dialog
        self.obstacle_sidebar = ObstacleSidebar(environment, size_input_dialog) # Create the sidebar


    def add_buttons(self):
        """Adds the buttons to the Environment window."""
        self.add_start_button()
        self.add_goal_button()
        self.add_obstacle_button()
        self.add_edit_limits_button()
        self.add_save_button()


    def add_start_button(self):
        start_button = QPushButton("Set Start Point")
        start_button.clicked.connect(self.get_start_point)
        self._add_to_layout(start_button)

    def add_goal_button(self):
        goal_button = QPushButton("Set Goal Point")
        goal_button.clicked.connect(self.get_goal_point)
        self._add_to_layout(goal_button)

    def add_obstacle_button(self):
        obstacle_button = QPushButton("Add Obstacle")
        obstacle_button.clicked.connect(self.get_obstacle_data)
        self._add_to_layout(obstacle_button)

    def add_edit_limits_button(self):
        """Adds the 'Edit Map Limits' button."""
        edit_limits_button = QPushButton("Edit Map Limits")
        edit_limits_button.clicked.connect(self.edit_map_limits)
        self._add_to_layout(edit_limits_button)

    def add_save_button(self):
        save_button = QPushButton("Save Map")
        save_button.clicked.connect(self.save_map)
        self._add_to_layout(save_button)

    def _add_to_layout(self, widget):
        """Helper function to add a widget to the layout."""
        central_widget = self.environment.centralWidget()
        if central_widget:
            layout = central_widget.layout()
            if layout:
                layout.addWidget(widget)
            else:
                print("Error: No layout found in central widget.")
        else:
            print("Error: No central widget found.")

    def get_start_point(self):
        dialog = StartPointDialog(self.environment.size)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            try:
                x, y, z = dialog.get_coordinates()

                # Validate position (within bounds)
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
        dialog = GoalPointDialog(self.environment.size)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            try:
                x, y, z = dialog.get_coordinates()

                # Validate position (within bounds)
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
        """Gets obstacle data, adds it to the environment, and updates the sidebar."""
        dialog = ObstacleDialog(self.environment.size, self.size_input_dialog.next_obstacle_id)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            try:
                obstacle_id, pos, size, color = dialog.get_obstacle_data()

                # Validate position (within bounds)
                if not (self.environment.size[0][0] <= pos[0] <= self.environment.size[0][1] and
                        self.environment.size[1][0] <= pos[1] <= self.environment.size[1][1] and
                        self.environment.size[2][0] <= pos[2] <= self.environment.size[2][1]):
                    QMessageBox.warning(self.environment, "Out of Bounds", "Obstacle position is outside the environment bounds.")
                    return

                # Validate size (positive)
                if any(s <= 0 for s in size):
                    QMessageBox.warning(self.environment, "Invalid Size", "Obstacle size must be positive.")
                    return

                self.environment.obstacles.append([obstacle_id, pos, size, color])
                self.size_input_dialog.next_obstacle_id += 1
                self.environment.updateView()
                self.obstacle_sidebar.update_obstacle_list()
                
            except ValueError as e:
                QMessageBox.critical(self.environment, "Error", str(e))

    def edit_obstacle(self, obstacle_data):
        """Edits the selected obstacle."""
        dialog = ObstacleDialog(self.environment.size, obstacle_data=obstacle_data)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            try:
                obstacle_id, pos, size, color = dialog.get_obstacle_data()

                # Validate position (within bounds)
                if not (self.environment.size[0][0] <= pos[0] <= self.environment.size[0][1] and
                        self.environment.size[1][0] <= pos[1] <= self.environment.size[1][1] and
                        self.environment.size[2][0] <= pos[2] <= self.environment.size[2][1]):
                    QMessageBox.warning(self.environment, "Out of Bounds", "Obstacle position is outside the environment bounds.")
                    return

                # Validate size (positive)
                if any(s <= 0 for s in size):
                    QMessageBox.warning(self.environment, "Invalid Size", "Obstacle size must be positive.")
                    return
                
                # Find and update the obstacle in the environment's obstacle list.
                for i, data in enumerate(self.environment.obstacles):
                    if data[0] == obstacle_id:
                        self.environment.obstacles[i] = [obstacle_id, pos, size, color]
                        break

                self.environment.updateView()
                self.obstacle_sidebar.update_obstacle_list()


            except ValueError as e:
                QMessageBox.critical(self.environment, "Error", str(e))

    def delete_obstacle(self, obstacle_data):
        """Deletes the selected obstacle."""
        obstacle_id = obstacle_data[0]

        index_to_remove = -1
        for i, data in enumerate(self.environment.obstacles):
            if data[0] == obstacle_id:
                index_to_remove = i
                break

        if index_to_remove != -1:
            del self.environment.obstacles[index_to_remove]
            self.environment.updateView()
            self.obstacle_sidebar.update_obstacle_list()

    def edit_map_limits(self):
        """Opens a dialog to edit the map limits and updates the environment."""
        dialog = EditLimitsDialog(self.environment.size)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            try:
                new_size = dialog.get_new_size()
                self.environment.size = new_size
                self.environment.updateView()

            except ValueError as e:
                QMessageBox.critical(self.environment, "Error", str(e))

    def save_map(self):
        """Saves the current map configuration."""
        map_saver = MapSaver(self.environment)
        map_saver.save_map()