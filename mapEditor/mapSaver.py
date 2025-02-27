from PyQt5.QtWidgets import QFileDialog, QMessageBox
import json
import os

class MapSaver:
    def __init__(self, environment):
        self.environment = environment

    def is_point_inside_obstacle(self, point, obstacle):
        """Checks if a point is inside an obstacle."""
        _, obs_pos, obs_size, _ = obstacle
        x, y, z = point
        obs_x, obs_y, obs_z = obs_pos
        size_x, size_y, size_z = obs_size

        half_size_x = size_x / 2
        half_size_y = size_y / 2
        half_size_z = size_z / 2

        # Check if the point is within the obstacle's bounds
        if (obs_x - half_size_x <= x <= obs_x + half_size_x and
            obs_y - half_size_y <= y <= obs_y + half_size_y and
            obs_z - half_size_z <= z <= obs_z + half_size_z):
            return True
        return False

    def save_map(self):
        """Saves the current map configuration to a file."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self.environment, "Save Map", "./maps/", "JSON Files (*.json)", options=options)

        if file_name:
            if not file_name.endswith(".json"):
                file_name += ".json"

            # --- Check for Start/Goal positions ---
            if self.environment.start is None:
                QMessageBox.critical(self.environment, "Error Saving Map", "Start position is not set!")
                return
            
            if self.environment.goal is None:
                QMessageBox.critical(self.environment, "Error Saving Map", "Goal position is not set!")
                return

            # --- Check for Start/Goal inside Obstacles ---
            if self.environment.start:
                for obstacle in self.environment.obstacles:
                    if self.is_point_inside_obstacle(self.environment.start, obstacle):
                        QMessageBox.critical(self.environment, "Error Saving Map", "Start point is inside an obstacle!")
                        return

            if self.environment.goal:
                for obstacle in self.environment.obstacles:
                    if self.is_point_inside_obstacle(self.environment.goal, obstacle):
                        QMessageBox.critical(self.environment, "Error Saving Map", "Goal point is inside an obstacle!")
                        return

            # --- Proceed with saving if checks pass ---
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
                QMessageBox.information(self.environment, "Map Saved", f"Map saved to {file_name}")
            except Exception as e:
                QMessageBox.critical(self.environment, "Error Saving Map", str(e))