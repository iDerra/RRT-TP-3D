from PyQt5.QtWidgets import (QListWidget, QListWidgetItem, QDockWidget, QMenu, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class ObstacleSidebar:
    def __init__(self, environment, size_input_dialog):
        self.environment = environment
        self.size_input_dialog = size_input_dialog
        self.obstacle_list_widget = QListWidget()
        self.dock_widget = None
        self.create_sidebar()

    def create_sidebar(self):
        """Adds a sidebar to display the list of obstacles."""
        self.obstacle_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.obstacle_list_widget.customContextMenuRequested.connect(self.show_obstacle_context_menu)
        self.dock_widget = QDockWidget("Obstacles", self.environment)
        self.dock_widget.setWidget(self.obstacle_list_widget)
        self.environment.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
        self.dock_widget.setMinimumWidth(200)

    def show_obstacle_context_menu(self, position):
        """Shows the context menu for the obstacle list."""
        item = self.obstacle_list_widget.itemAt(position)
        if item is None:
            return

        obstacle_data = item.data(Qt.UserRole)
        menu = QMenu()

        edit_action = QAction("Edit Obstacle", menu)
        delete_action = QAction("Delete", menu)

        edit_action.triggered.connect(lambda: self.size_input_dialog.button_manager.edit_obstacle(obstacle_data))
        delete_action.triggered.connect(lambda: self.size_input_dialog.button_manager.delete_obstacle(obstacle_data))

        menu.addAction(edit_action)
        menu.addAction(delete_action)

        menu.exec_(self.obstacle_list_widget.mapToGlobal(position))

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