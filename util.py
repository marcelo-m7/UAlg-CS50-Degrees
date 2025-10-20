import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import time


class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action


class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node


def visualize_path(path, people, movies):
    """
    Visualizes the shortest path as a pandas DataFrame.
    """
    if len(path) <= 1:
        print("No connections to display.")
        return

    data = []
    for i in range(1, len(path)):
        person1 = people[path[i-1][1]]["name"]
        person2 = people[path[i][1]]["name"]
        movie = movies[path[i][0]]["title"]
        data.append({"Step": i, "Person1": person1, "Movie": movie, "Person2": person2})

    df = pd.DataFrame(data)
    print("Degrees of Separation Path:")
    print(df.to_string(index=False))


def visualize_path_as_graph(path, people, movies):
    """
    Visualizes the shortest path as a NetworkX graph and saves a plot.
    """
    if len(path) <= 1:
        print("No connections to display.")
        return

    G = nx.Graph()
    for i in range(1, len(path)):
        person1 = people[path[i-1][1]]["name"]
        person2 = people[path[i][1]]["name"]
        movie = movies[path[i][0]]["title"]
        G.add_edge(person1, person2, movie=movie)

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=10, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): d['movie'] for u, v, d in G.edges(data=True)})
    plt.title("Degrees of Separation Graph")
    plt.savefig("degrees_graph.png")
    print("Graph saved as degrees_graph.png")


def measure_execution_time(func, *args, **kwargs):
    """
    Measures the execution time of a given function.
    
    Args:
        func: The function to measure.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.
    
    Returns:
        tuple: (result of func, execution time in seconds)
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    return result, execution_time
