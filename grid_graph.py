
'''
/* =======================================================================
   (c) 2015, Kre8 Technology, Inc.

   Name:          grid_graph_starter.py
   By:            Qin Chen
   Last Updated:  6/10/18
    
   Definition of class GridGraph. Description of all the methods is
   provided. Students are expected to implement the methods for Lab#6.
   ========================================================================*/
'''
import Tkinter as tk
from grid_graph_display import *

class GridGraph(object):
    def __init__(self):
        self.nodes = {} # {node_name: set(neighboring nodes), ...}
        self.startNode = None  # string
        self.goalNode = None    # string
        self.grid_rows = None
        self.grid_columns = None
        self.obs_list = []
        self.node_display_locations=[]
        return

    # set number of rows in the grid
    def set_grid_rows(self, rows):
        self.grid_rows = rows

    # set number of columns in the grid
    def set_grid_cols(self, cols):
        self.grid_columns = cols

    # this method is used by make_grid() to create a key-value pair in self.nodes{},
    # where value is created as an empty set which is populated later while connecting
    # nodes.
    def add_node(self, name):
        self.nodes[name] = set([])

    # set start node name
    def set_start(self, name):
        self.startNode = name

    # returns start node name
    def get_start_node(self):
        return self.startNode

    # set goal node name
    def set_goal(self, name):
        self.goalNode = name

    # return goal node name
    def get_goal_node(self):
        return self.goalNode

    # Given two neighboring nodes. Put them to each other's neighbors-set. This
    # method is called by self.connect_nodes() 
    def add_neighbor(self, node1, node2):
        self.nodes[node2].add(node1)
        self.nodes[node1].add(node2)

    # populate graph with all the nodes in the graph, excluding obstacle nodes
    def make_grid(self):
        for col in range(0, self.grid_columns):
            for row in range(0, self.grid_rows):
                if [col, row] not in self.obs_list:
                    self.add_node(str(col)+"-"+str(row))

    # Based on node's name, this method identifies its neighbors and fills the 
    # set holding neighbors for every node in the graph.
    def connect_nodes(self):
        for col in range(0, self.grid_columns):
            for row in range (0, self.grid_rows):
                if [col,row] not in self.obs_list:
                    if row+1 < self.grid_rows and [col, row+1] not in self.obs_list:
                        self.add_neighbor(str(col)+"-"+str(row), str(col)+"-"+str(row+1))
                    if col+1 < self.grid_columns and [col+1, row] not in self.obs_list:
                        self.add_neighbor(str(col)+"-"+str(row), str(col+1)+"-"+ str(row))


    # For display purpose, this function computes grid node location(i.e., offset from upper left corner where is (1,1)) 
    # of display area. based on node names.
    # Node '0-0' is displayed at bottom left corner 
    def compute_node_locations(self):
        for col in range(0, self.grid_columns):
            for row in range(0, self.grid_rows):
                if [col, row] not in self.obs_list:
                    self.node_display_locations.append([col,row])
        

###########################################################
#  A testing program of your implementaion of GridGraph class.
###########################################################
def main():
    graph = GridGraph()
    # grid dimension
    graph.set_grid_rows(4)
    graph.set_grid_cols(3)

    # origin of grid is (0, 0) lower left corner
    # graph.obs_list = ([1,1],)    # in case of one obs. COMMA
    graph.obs_list = ([1,1], [3,0], [2,2])
    
    graph.set_start('0-0')
    graph.set_goal('2-1')
    
    graph.make_grid()
    graph.connect_nodes()

    root = tk.Tk()
    graphDisplay = GridGraphDisplay(root, graph)
    graphDisplay.display_graph()
    root.mainloop()

    for node in graph.nodes:
        print node + " " + str(graph.nodes[node])




    return

if __name__ == "__main__":
    main()