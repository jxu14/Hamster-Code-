# Robot Programming
# breadth first search
# by Dr. Qin Chen
# May, 2016

import sys
import Tkinter as tk

from bfs import *
##############
# This class supports display of a grid graph. The node location on canvas
# is included as a data field of the graph, graph.node_display_locations.
##############

class GridGraphDisplay(object):
    def __init__(self, frame, graph,HIN,WIN):
        self.node_size = 60
        self.node_dist = self.node_size*1.5
        self.gui_root = frame
        self.canvas = None
        self.graph = graph
        self.nodes_location = graph.node_display_locations
        self.start_node = graph.startNode
        self.goal_node = graph.goalNode

        self.canvas = tk.Canvas(self.gui_root, width = str(WIN*self.node_size + WIN*self.node_dist), height = str(HIN*self.node_size + HIN*self.node_dist));
        self.canvas.pack();
        self.heightInNode = HIN;

        return

    # draws nodes and edges in a graph
    def display_graph(self):
        
        for node in self.nodes_location:
            self.draw_node(node, 'blue')
        self.canvas.pack()
        bfs = BFS(self.graph);
        path = bfs.bfs_shortest_path(self.start_node,self.goal_node);
        newPath = []
        for i in range (0,len(path)):
            path[i] = path[i].split("-");
            newPath.append([path[i][0],path[i][1]])
        self.highlight_path(newPath);
        sn = self.start_node.split("-")
        en = self.goal_node.split("-")
        self.draw_node(sn, 'green')
        self.draw_node(en, 'red')

        
        for i in range (0,(len(path)-1)):
            self.draw_edge(path[i],path[i+1], 'orange')
    
    # path is a list of nodes ordered from start to goal node
    def highlight_path(self, path):
        for node in path:
            print node
            self.draw_node(node, 'orange')
    
  
    # draws a node in given color. The node location info is in passed-in node object
    def draw_node(self, node, n_color):
        x = int(node[0])
        y = int(node[1])+1
        space = self.node_size*1.5;
        offset = self.node_dist;
        inversion = space * self.heightInNode;
        node = self.canvas.create_oval(x*space+offset, inversion - y*space+offset,x*space+offset+self.node_size,inversion - y*space+offset+self.node_size,fill=n_color);
        

    # draws an line segment, between two given nodes, in given color
    def draw_edge(self, node1, node2, e_color):
        x1 = int(node1[0])
        y1 = int(node1[1])+1
        x2 = int(node2[0])
        y2 = int(node2[1])+1
        space = self.node_size*1.5;
        offset = self.node_dist;
        inversion = space * self.heightInNode;
        edge = self.canvas.create_line(x1*space+offset+self.node_size/2.0, inversion - y1*space+offset+self.node_size/2.0,x2*space+offset+self.node_size/2.0,inversion - y2*space+offset+self.node_size/2.0);
    