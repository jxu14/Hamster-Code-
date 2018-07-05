'''
/* =======================================================================
   (c) 2015, Kre8 Technology, Inc.

   Name:          bfs_engine.py
   By:            Qin Chen
   Last Updated:  6/10/18

   PROPRIETARY and CONFIDENTIAL
   ========================================================================*/
'''
import sys

class BFS(object):
    def __init__(self, graph):
        self.graph = graph
        return

    ######################################################
    # this function returns the shortest path for given start and goal nodes
    ######################################################
    def bfs_shortest_path(self, start, goal):
        stack = [(start, [start])]
        while stack:
            (node, path) = stack.pop(0)
            print '\n visitng node', node, 'path= ', path
            for next in (self.graph[node] - set(path)):
                print 'next node', next
                if next == goal:
                    return path+[next]
                else:
                    stack.append((next, path + [next]))
                    print "Stack push ", next, path + [next]

        return

    ######################################################
    # this function returns all paths for given start and goal nodes
    ######################################################
    def bfs_paths(self, start, goal):
        paths = []

        stack = [(start, [start])]
        while stack:
            (node, path) = stack.pop()
            #print '\n visitng node', node, 'path= ', path
            for next in (self.graph[node] - set(path)):
                #print 'next node', next
                if next == goal:
                    paths.append(path+[next])
                else:
                    stack.append((next, path + [next]))


        return paths






                
    #########################################################
    # This function returns the shortest paths for given list of paths
    #########################################################
    def shortest(self, paths):
        smallestLength = paths[0]
        shortestPath = 0

        for singlePath in paths:
            if len(singlePath) < smallestLength:
                smallestLength = len(singlePath)
                shortestPath = singlePath

        return singlePath


    #########################################################
    # THis function traverses the graph from given start node
    # return order of nodes visited
    #########################################################
    def bfs(self, start):
        visited_order = list()
        visited = set()
        q = list([start])

        while q:
            node = q.pop(0)
            if node not in visited:
                print("visiting ", node)
                visited.add(node)
                visited_order.append(node)
                print("--visited_order ", visited_order)
                q.extend(self.graph[node] - visited)

        return visited_order

def main():
    graph = {'A': set(['B', 'C']),
        'B': set(['A', 'C', 'D', 'E']),
        'C': set(['A', 'B', 'D', 'G']),
        'D': set(['B', 'C', 'E', 'G']),
        'E': set(['B', 'D', 'F', 'G']),
        'F': set(['E','G']),
        'G': set(['C', 'D', 'E', 'F'])}
    bfs = BFS(graph)
    start_node = 'A'
    end_node = 'G'

    p = bfs.bfs_shortest_path(start_node, end_node)
    print "\n++++++++++Shortest path from %s to %s: %s\n" % (start_node, end_node, p)
    
    #find all the paths returned by bfs_paths()
    paths = list(bfs.bfs_paths(start_node, end_node)) # [['A', 'C', 'F'], ['A', 'B', 'E', 'F']]
    print "\n==========paths from %s to %s: %s\n" % (start_node, end_node, paths)
    print len(paths)
    print "\n----------shortest path: %s\n" % bfs.shortest(paths)

    # order holds traverse order of the all the nodes
    order = bfs.bfs(start_node)
    print "\n##########traverse order:", order

    return


if __name__ == "__main__":
    sys.exit(main())