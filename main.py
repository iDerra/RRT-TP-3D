from environment import *
from rrt import *
from PyQt5.QtWidgets import QApplication
import sys

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

app = QApplication(sys.argv)
size = [(-3,3),(-2,4),(-1,4)]
obs = [(-2,1,0),(1,1.5,1.5)]
obs_sizes = [(3,0.5,3), (1,1.5,1.5)]
obs_colors = [(1,0,0,1),(1,0,0,1)]
start = [1,-0.5,0.30]
goal = [2.5,3.5,1.0]

env_settings = EnvSettings()
env = Environment(size, obs, obs_sizes, obs_colors, start, goal, env_settings)

rrt_settings = RRTSettings()
waypoints = search(env.size, start, goal, obs, obs_sizes, rrt_settings, nTests=0)
env.plotTrajectory(waypoints)

env.show()
sys.exit(app.exec_())


