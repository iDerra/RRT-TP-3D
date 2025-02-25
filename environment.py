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
    def __init__(self, grid=True, startColor=(0, 1, 0, 1), goalColor=(0, 0, 1, 1), obstacleColor=(1, 0, 0, 1), boundary=True):
        self.grid = grid
        self.startColor = startColor
        self.goalColor = goalColor
        self.obstacleColor = obstacleColor
        self.boundary = boundary

class Environment(QMainWindow):
    """
    Creates the main window for displaying the RRT environment.

    :param size: The dimensions of the environment (width, length, height).
    :param obs: A list of obstacle coordinates (x, y, z).
    :param obs_sizes: A list of obstacle sizes (width, length, height).
    :param obs_colors: A list of obstacle colors (RGBA).
    :param start: The starting position (x, y, z).
    :param goal: The goal position (x, y, z).
    :param settings: An object containing environment display settings.
    :type settings: `EnvSettings`
    """
    def __init__(self, size, obs, obs_sizes, obs_colors, start, goal, settings):
        super().__init__()
        self.setWindowTitle("RRT Environment Viewer")
        self.setGeometry(100, 100, 800, 800)

        self.size = size
        self.start = start
        self.goal = goal
        self.obstacles = list(zip(obs, obs_sizes, obs_colors))
        self.trajectory = None
        self.settings = settings

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
        self.view.clear()

        if self.settings.grid:
            grid = GLGridItem()
            grid.scale(1, 1, 1)
            grid.setColor((0,0,0,255))
            self.view.addItem(grid)

        if self.settings.boundary:
            self.create_boundary()        

        if self.start:
            self.create_cube(self.start, (0.2, 0.2, 0.2), self.settings.startColor)

        if self.goal:
            self.create_cube(self.goal, (0.2, 0.2, 0.2), self.settings.goalColor)

        for (pos, size, color) in self.obstacles:
            if color is None:
                self.create_cube(pos, size, self.settings.obstacleColor)
            else:
                self.create_cube(pos, size, color)

        if self.trajectory is not None:
            trajectory_line = GLLinePlotItem(pos=self.trajectory, color=(0, 0, 0, 1), width=8, antialias=True)
            self.view.addItem(trajectory_line)

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

        # Create the filled mesh (without shadows)
        mesh = GLMeshItem(vertexes=verts, faces=faces, smooth=True, color=color, drawEdges=False, glOptions='opaque')
        self.view.addItem(mesh)

        # Create edges as separate lines
        edges = np.array([
            [0, 1], [1, 2], [2, 3], [3, 0],
            [4, 5], [5, 6], [6, 7], [7, 4],
            [0, 4], [1, 5], [2, 6], [3, 7]
        ], dtype=np.int32)

        for edge in edges:
            line = GLLinePlotItem(pos=verts[edge], color=(0, 0, 0, 1), width=2, antialias=True) #Black edges
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
        Plots the trajectory (path) in the environment.

        :param waypoints: A list of 3D points (x, y, z) representing the waypoints of the trajectory.
        """
        self.trajectory = np.array(waypoints, dtype=np.float32)
        self.updateView()