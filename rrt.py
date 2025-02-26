import random as rd
import numpy as np

def search(size, start, goal, obs, rrt_settings, nTests = 0):
    """
    Performs a search using the RRT algorithm.

    :param size: The dimensions of the environment (width, length, height).
    :param start: The starting position (x, y, z).
    :param goal: The goal position (x, y, z).
    :param obs: A list of obstacle positions (x, y, z).
    :param obs_sizes: A list of obstacle sizes (width, length, height).
    :param rrt_settings: Settings for the RRT algorithm.
    :type rrt_settings: `RRTSettings`
    :param nTests: The number of times to run the algorithm for testing. Defaults to 0.
    :return: A list of waypoints representing the path found by the RRT algorithm, or an empty list if no path is found.
    """

    rrt_class = RRT(size, start, goal, obs, rrt_settings)
    
    #This code runs x times the algorithm and store the amount of waypoints created in a file.
    if nTests > 0: 
        file=open("testLog.log","a")
        file.write("New Test\n")
        file.close()
        for i in range(0,nTests):
            file=open("testLog.log","a")

            waypoints, total = rrt_class.main_logic()
            print(f"{i+1}/{nTests}")
            file.write(f"{i+1}/{nTests} - Nodes: "+str(total)+"\n")

            file.close()
    else:
        waypoints, _ = rrt_class.main_logic()
    
    return waypoints

# --- RRT --- #

class RRTSettings(object):
    """
    Represents the settings for the RRT (Rapidly-exploring Random Tree) algorithm.

    Modifying some of these values may cause collisions, not reaching the target or other major problems, so only modify them if you know what you are doing.

    :param safeDistance: The minimum safe distance to maintain from obstacles. Defaults to 1.75.
    :param goalDistance: The distance threshold to consider a node as reaching the goal. Defaults to 0.3.
    :param nodeDistance: The maximum distance between nodes in the tree. Defaults to 0.3.
    :param nodeLimit: The maximum number of nodes to generate before stopping. Defaults to 5000.
    :param quadrants: Whether to use quadrant-based sampling. Defaults to False.
    :param numQuadrantsPerAxis: The number of quadrants per axis if quadrant-based sampling is enabled. Defaults to 2.
    :param quadrantProb: The probability of sampling from a quadrant (as opposed to the whole space). Defaults to 0.5.
    """
    def __init__(self, safeDistance=1.75, goalDistance=0.3, nodeDistance=0.3, nodeLimit=5000, quadrants=False, numQuadrantsPerAxis=2, quadrantProb=0.5):
        self.safeDistance = safeDistance
        self.goalDistance = goalDistance
        self.nodeDistance = nodeDistance
        self.nodeLimit = nodeLimit
        self.quadrants = quadrants
        self.numQuadrantsPerAxis= numQuadrantsPerAxis
        self.quadrantProb = quadrantProb

class RRT(object):
    """
    Represents the RRT (Rapidly-exploring Random Tree) algorithm for path planning.

    :param size: The dimensions of the environment (min_x, max_x), (min_y, max_y), (min_z, max_z).
    :param start: The starting position (x, y, z).
    :param goal: The target (goal) position (x, y, z).
    :param obs: A list of obstacle positions (x, y, z).
    :param obs_sizes: A list of obstacle sizes (width, length, height).
    :param settings: Settings for the RRT algorithm.
    :type settings: RRTSettings
    """
    def __init__(self, size, start, goal, obs, settings):
        self.size = size
        self.start = start
        self.goal = goal
        self.obs = []
        self.obs_sizes = []
        self.use_quadrants = settings.quadrants
        self.settings = settings

        for obstacle in obs:
            _, obs, size, _ = obstacle
            self.obs.append(obs)
            self.obs_sizes.append(size)

        if settings.quadrants:
            self.quadrant_prob = settings.quadrantProb
            self.num_quadrants_per_axis = settings.numQuadrantsPerAxis
            self.num_quadrants = settings.numQuadrantsPerAxis**3
            self.quadrants = self.__create_quadrants()
            self.t_quadrant = None

    def __create_quadrants(self):
        """
        Creates quadrants dynamically based on environment size and settings.
        return: A list of quadrants, where each quadrant is represented by two tuples:
                ((min_x, min_y, min_z), (max_x, max_y, max_z)).
        """
        quadrants = []
        x_step = (self.size[0][1] - self.size[0][0]) / self.num_quadrants_per_axis
        y_step = (self.size[1][1] - self.size[1][0]) / self.num_quadrants_per_axis
        z_step = (self.size[2][1] - self.size[2][0]) / self.num_quadrants_per_axis

        for _ in range(self.num_quadrants_per_axis):
            for _ in range(self.num_quadrants_per_axis):
                for _ in range(self.num_quadrants_per_axis):
                    x_start = self.size[0][0] + _ * x_step
                    x_end = x_start + x_step
                    y_start = self.size[1][0] + _ * y_step
                    y_end = y_start + y_step
                    z_start = self.size[2][0] + _ * z_step
                    z_end = z_start + z_step
                    quadrants.append((
                        (x_start, y_start, z_start),
                        (x_end, y_end, z_end)
                    ))
        return quadrants

    def __check_quadrant(self, node, quadrant):
        """
        Checks if a node is within a given quadrant.

        :param node: The node to check (x, y, z).
        :param quadrant: The quadrant to check against, represented by two tuples: ((min_x, min_y, min_z), (max_x, max_y, max_z)).
        :return: True if the node is within the quadrant, False otherwise.
        """
        x, y, z = node
        qx_min, qy_min, qz_min = quadrant[0]
        qx_max, qy_max, qz_max = quadrant[1]
        return qx_min <= x <= qx_max and qy_min <= y <= qy_max and qz_min <= z <= qz_max

    def __create_new_node(self):
        """
        Creates a new random node, with optional bias towards the goal quadrant.

        :return: The new node's coordinates [x, y, z].
        """
        if self.use_quadrants:
            if self.t_quadrant is None:
                for i, quad in enumerate(self.quadrants):
                    if self.__check_quadrant(self.goal, quad):
                        self.t_quadrant = i
                        break
            if self.t_quadrant is not None and rd.random() < self.quadrant_prob:
                quadrant = self.quadrants[self.t_quadrant]
                x = rd.uniform(quadrant[0][0], quadrant[1][0])
                y = rd.uniform(quadrant[0][1], quadrant[1][1])
                z = rd.uniform(quadrant[0][2], quadrant[1][2])
                return [x, y, z]

        x = rd.uniform(self.size[0][0], self.size[0][1])
        y = rd.uniform(self.size[1][0], self.size[1][1])
        z = rd.uniform(self.size[2][0], self.size[2][1])
        return [x, y, z]

    def __check_obstacles(self, initial, objective, center, size):
        """
        Checks for collisions between a line segment and an obstacle.

        :param initial: The starting point of the line segment (x, y, z).
        :param objective: The ending point of the line segment (x, y, z).
        :param center: The center of the obstacle (x, y, z).
        :param size: The size of the obstacle (width, length, height).
        :return: True if there is a collision, False otherwise.
        """
        p1 = np.array(initial)
        p2 = np.array(objective)
        v = p2 - p1

        half_size = np.array(size) / 2 * self.settings.safeDistance

        min_vertex = np.array(center) - half_size
        max_vertex = np.array(center) + half_size

        t_min = -np.inf
        t_max = np.inf

        for i in range(3):
            if v[i] == 0:
                if p1[i] < min_vertex[i] or p1[i] > max_vertex[i]:
                    return True
            else:
                t1 = (min_vertex[i] - p1[i]) / v[i]
                t2 = (max_vertex[i] - p1[i]) / v[i]
                t_min = max(t_min, min(t1, t2))
                t_max = min(t_max, max(t1, t2))

        if t_min > t_max or t_max < 0 or t_min > 1:
            return False
        else:
            return True

    def __calculate_distance(self, p1, p2):
        """
        Calculates the Euclidean distance between two points.

        :param p1: The first point (x, y, z).
        :param p2: The second point (x, y, z).
        :return: The Euclidean distance between the two points.
        """
        return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2)

    def __check_distance(self, actual_node, new_node, max_dist):
        """
        Checks the distance between two nodes and creates an intermediate node if necessary.

        :param actual_node: The current node (x, y, z).
        :param new_node: The new node (x, y, z).
        :param max_dist: The maximum allowed distance between nodes.
        :return: The new node, potentially adjusted to be within the maximum distance.
        """
        vector = np.array(new_node) - np.array(actual_node)
        distance = np.linalg.norm(vector)

        if distance <= max_dist:
            return new_node
        else:
            unit_vector = vector / distance
            new_waypoint = np.array(actual_node) + max_dist * unit_vector
            return list(new_waypoint)

    def main_logic(self):
        """
        The main logic of the RRT algorithm.

        :return: A tuple containing:
            - A list of waypoints representing the path found (or an empty list if no path is found).
            - The total number of nodes generated.
        """
        completed = False
        label = 0
        root_label = 0
        rwp = []
        waypoints = []
        center_obs = []

        waypoints.append([list(self.start), label, root_label])

        for obs, size in zip(self.obs, self.obs_sizes):
            center = np.array(obs) + np.array(size) / 2
            center_obs.append(center)

        while not completed:
            label += 1
            if label > self.settings.nodeLimit:  # Check if maximum nodes reached
                print("Maximum nodes reached. Returning current path.")
                break  # Exit the loop

            new_node = self.__create_new_node()

            nearest_dist = float('inf')
            nearest_waypoint = None
            nearest_label = None

            for waypoint in waypoints:
                dist = self.__calculate_distance(waypoint[0], new_node)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_waypoint = waypoint[0]
                    nearest_label = waypoint[1]

            if nearest_waypoint is None:
                continue

            new_waypoint = self.__check_distance(nearest_waypoint, new_node, self.settings.nodeDistance)

            collision = False
            for i in range(len(self.obs)):
                if self.__check_obstacles(nearest_waypoint, new_waypoint, center_obs[i], self.obs_sizes[i]):
                    collision = True
                    break

            if collision:
                continue

            waypoints.append([list(new_waypoint), label, nearest_label])

            if self.__calculate_distance(new_waypoint, self.goal) < self.settings.goalDistance:
                print("Goal reached")
                completed = True
                back_waypoint = waypoints[-1]
                print("Number of nodes:", len(waypoints))

                while back_waypoint[1] != back_waypoint[2]:
                    rwp.append(list(back_waypoint[0]))
                    for tmp_waypoint in waypoints:
                        if tmp_waypoint[1] == back_waypoint[2]:
                            back_waypoint = tmp_waypoint
                            break
                rwp.append(list(back_waypoint[0]))
                rwp.reverse()
                return rwp, len(waypoints)
        
        if len(waypoints) > 0: 
            back_waypoint = waypoints[-1]
            while back_waypoint[1] != back_waypoint[2]:
                rwp.append(list(back_waypoint[0]))
                for tmp_waypoint in waypoints:
                    if tmp_waypoint[1] == back_waypoint[2]:
                        back_waypoint = tmp_waypoint
                        break
            rwp.append(list(back_waypoint[0]))
            rwp.reverse()
            return rwp, len(waypoints)
        else:
            return [], 0