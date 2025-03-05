import numpy as np
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from pyqtgraph.opengl import GLViewWidget, GLGridItem, GLMeshItem, GLLinePlotItem

class EnvSettings(object):
    """
    Settings of the environment

    :param grid: Indicates whether to display a grid. Defaults to True.
    :param startColor: The color of the starting point (RGBA format). Defaults to (0, 1, 0, 1).
    :param goalColor: The color of the goal point (RGBA format). Defaults to (0, 0, 1, 1).
    :param obstacleColor: The color of obstacles (RGBA format). Defaults to (1, 0, 0, 1).
    :param boundary: Indicates whether to display a boundary. Defaults to True.
    """
    def __init__(self, grid=True, startColor=(0, 1, 0, 1), goalColor=(0, 0, 1, 1), obstacleColor=(1, 0, 0, 1), boundary=True, displayResolution=(1920, 1080)):
        self.grid = grid
        self.startColor = startColor
        self.goalColor = goalColor
        self.obstacleColor = obstacleColor
        self.boundary = boundary
        self.displayResolution = displayResolution

class Environment(QMainWindow):
    """
    Creates the main window for displaying the RRT environment.

    :param size: The dimensions of the environment (width, length, height).
    :param obs: A list of obstacles.
    :param start: The starting position (x, y, z).
    :param goal: The goal position (x, y, z).
    :param settings: An object containing environment display settings.
    :type settings: `EnvSettings`
    """
    def __init__(self, size, obs, start, goal, settings):
        super().__init__()
        self.setWindowTitle("RRT Environment Viewer")
        self.Hresolution = int(settings.displayResolution[0]*0.5)
        self.Vresolution = int(settings.displayResolution[1]*0.8)

        self.setGeometry(100, 100, self.Hresolution, self.Vresolution)
        self.size = size
        self.start = start
        self.goal = goal
        self.obstacles = obs
        self.trajectory = None
        self.settings = settings
        self.trajectory_items = []

        self.__initUI()

    def __initUI(self):
        """
        Initializes the user interface components of the environment window.

        Sets up the OpenGL view widget, layout, and central widget.  Calls `updateView` to populate the initial scene.
        """
        self.view = GLViewWidget()
        self.view.setCameraPosition(distance=20)
        self.view.setBackgroundColor('w')

        layout = QVBoxLayout()
        layout.addWidget(self.view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.updateView()

    def updateView(self):
        """
        Updates the view of the environment.

        Clears the existing view and redraws all elements based on the current settings and data:
        grid, boundary, start/goal points, obstacles, and trajectory.
        """

        if self.settings.grid:
            grid = self.add_grid()
            self.view.addItem(grid)

        if self.settings.boundary:
            self.create_boundary()        

        if self.start:
            self.create_cube(self.start, (0.2, 0.2, 0.2), self.settings.startColor)

        if self.goal:
            self.create_cube(self.goal, (0.2, 0.2, 0.2), self.settings.goalColor)

        for obstacle_data in self.obstacles:
            _, pos, size, color = obstacle_data
            if color is None:
                self.create_cube(pos, size, self.settings.obstacleColor)
            else:
                self.create_cube(pos, size, color)

        self.add_coordinate_axes()

    def add_grid(self):
        """Adds (or updates) the grid to the environment."""
        grid = GLGridItem()
        grid.setSize(x = abs(max(self.size[0]) - min(self.size[0])) + 4,y = abs(max(self.size[1]) - min(self.size[1])) + 4, z=1)
        grid.setSpacing(x=1, y=1, z=1) 
        grid.setColor((0, 0, 0, 255))

        center_x = (self.size[0][0] + self.size[0][1]) / 2
        center_y = (self.size[1][0] + self.size[1][1]) / 2
        grid.translate(center_x, center_y, 0)

        return grid
    
    def add_coordinate_axes(self):
        """Adds X, Y, and Z axes at (0, 0, 0)."""
        x_axis = GLLinePlotItem(pos=np.array([[0, 0, 0], [1, 0, 0]], dtype=np.float32), color=(1, 0, 0, 1), width=3, antialias=True)
        self.view.addItem(x_axis)

        y_axis = GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 1, 0]], dtype=np.float32), color=(0, 1, 0, 1), width=3, antialias=True)
        self.view.addItem(y_axis)

        z_axis = GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 0, 1]], dtype=np.float32), color=(0, 0, 1, 1), width=3, antialias=True)
        self.view.addItem(z_axis)

    def create_cube(self, pos, size, color):
        """
        Creates a cube in the 3D environment.

        :param pos: The center position of the cube (x, y, z).
        :param size: The dimensions of the cube (width, length, height).
        :param color: The color of the cube (RGBA).
        """
        x, y, z = pos
        sx, sy, sz = size

        verts = np.array([
            [x - sx/2, y - sy/2, z - sz/2],
            [x + sx/2, y - sy/2, z - sz/2],
            [x + sx/2, y + sy/2, z - sz/2],
            [x - sx/2, y + sy/2, z - sz/2],
            [x - sx/2, y - sy/2, z + sz/2],
            [x + sx/2, y - sy/2, z + sz/2],
            [x + sx/2, y + sy/2, z + sz/2],
            [x - sx/2, y + sy/2, z + sz/2],
        ], dtype=np.float32)
        faces = np.array([
            [0, 1, 2], [0, 2, 3],
            [4, 5, 6], [4, 6, 7],
            [0, 1, 5], [0, 5, 4],
            [2, 3, 7], [2, 7, 6],
            [1, 2, 6], [1, 6, 5],
            [0, 3, 7], [0, 7, 4]
        ],  dtype=np.int32)

        mesh = GLMeshItem(vertexes=verts, faces=faces, smooth=True, color=color, drawEdges=False, glOptions='opaque')
        self.view.addItem(mesh)

        edges = np.array([
            [0, 1], [1, 2], [2, 3], [3, 0],
            [4, 5], [5, 6], [6, 7], [7, 4],
            [0, 4], [1, 5], [2, 6], [3, 7]
        ], dtype=np.int32)

        for edge in edges:
            line = GLLinePlotItem(pos=verts[edge], color=(0, 0, 0, 1), width=2, antialias=True)
            self.view.addItem(line)

    def create_boundary(self):
        """
        Creates the boundary lines of the environment.

        The boundary is rendered as a set of red lines outlining the environment's extents.
        It uses the environment's `size` attribute to determine the boundary dimensions.
        """
        min_x, max_x = self.size[0]
        min_y, max_y = self.size[1]
        min_z, max_z = self.size[2]

        boundary_lines = np.array([
            [min_x, min_y, min_z], [max_x, min_y, min_z],
            [max_x, min_y, min_z], [max_x, max_y, min_z],
            [max_x, max_y, min_z], [min_x, max_y, min_z],
            [min_x, max_y, min_z], [min_x, min_y, min_z],

            [min_x, min_y, max_z], [max_x, min_y, max_z],
            [max_x, min_y, max_z], [max_x, max_y, max_z],
            [max_x, max_y, max_z], [min_x, max_y, max_z],
            [min_x, max_y, max_z], [min_x, min_y, max_z],

            [min_x, min_y, min_z], [min_x, min_y, max_z],
            [max_x, min_y, min_z], [max_x, min_y, max_z],
            [max_x, max_y, min_z], [max_x, max_y, max_z],
            [min_x, max_y, min_z], [min_x, max_y, max_z]
        ], dtype=np.float32)

        boundary = GLLinePlotItem(pos=boundary_lines, color=(1, 0, 0, 1), width=2, antialias=True)
        self.view.addItem(boundary)

    def plotTrajectory(self, waypoints):
        """
        Plots the trajectory (path) in the environment.  Adds to self.trajectory_items.

        :param waypoints: A list of 3D points (x, y, z) representing the waypoints of the trajectory.
        """
        trajectory_line = GLLinePlotItem(pos=np.array(waypoints, dtype=np.float32), color=(0, 0, 0, 1), width=8, antialias=True)
        self.view.addItem(trajectory_line)
        self.trajectory_items.append(trajectory_line)

    def clear_scene(self):
        """Clears only the trajectory lines from the scene."""
        for item in self.trajectory_items:
            self.view.removeItem(item)
        self.trajectory_items = []