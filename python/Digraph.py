#
# File:    Digraph.py
# Author:  Alex Stivala
# Created: October 2017
#
#
#
# Defines the directed graph structure Digraph with arc list graph
# representations including forward and reverse arc lists for
# fast traversal in computing change statistics.
#
#



class Digraph:
    """
    The network is represented as a dictionary of dictionaries.
    Nodes are indexed by integers 0..n-1. The outermost dictionary has the node
    v as a key, and dictionary as value. Then this dictionary has the neighbours
    of v as the keys, with the values as arc weights (or labels).
    This is the structure suggested by David Eppstein (UC Irvine) in
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/117228
    and as noted there it supprts easy modification by edge addition and
    removal, which is required by Algorithm EE.
    So G[i] is a dictionary with k entries, where k is the degree of node i.
    and G[i][j] exists exactly when j is a neighbour of i.
    And simple operations are:
      outdegree of node i:                   len(G[i])
      does arc i->j exist?:                  j in G[i]                 
      dict where keys are out-neighbours of i:  G[i]
      iterator over out-neighbourhood of i   G[i].iterkeys()
      in-place insert edge i->j:             G[i][j] = w [for some value w]
      in-place remove edge i->j:             G[i].pop(j) 
      copy of G (not modified when G is):    deepcopy(G)
      number of arcs:              sum([len(v.keys()) for v in G.itervalues()])
    To make these operations simple (no special cases for nodes with no
    neighbours),  the graph is initialized so that G[i] = dict() for
    all 0 <= i < n: dict(zip(range(n), [dict() for i in range(n)]))
    """

    def __init__(self, n):
        """
        Construct empty digraph with n nodes.

        Parameters:
            n - number of nodes.
        """
        self.G = None  # dict of dicts as described above
        self.Grev = None # version with all arcs reversed to get in-neighbours

        # empty graph n nodes        
        self.G = dict(zip(range(n), [dict() for i in range(n)]))
        self.Grev = dict(zip(range(n), [dict() for i in range(n)]))

    def numNodes(self):
        """
        Return number of nodes in digraph
        """
        return len(self.G)
    
    def numArcs(self):
        """
        Return number of arcs in digraph
        """
        return sum([len(v.keys()) for v in self.G.itervalues()])
    
    def density(self):
        """
        Return the digraph density 
        """
        edges = self.numArcs()
        nodes = self.numNodes()
        return float(edges) / float(nodes*(nodes-1))

    def outdegree(self, i):
        """
        Return Out-degree of node i
        """
        return len(self.G[i])

    def indegree(self, i):
        """
        Return In-degree of node i
        """
        return len(self.Grev[i])

    def isArc(self, i, j):
        """
        Return True iff arc i -> j in digraph
        """
        return j in self.G[i]

    def outIterator(self, i):
        """
        Return iterator over out-neighbours of i
        """
        return self.G[i].iterkeys()

    def inIterator(self, i):
        """
        Return iterator over in-neighbours of i
        """
        return self.Grev[i].iterkeys()

    def insertArc(self, i, j, w):
        """
        Insert arc i -> j with arc weight (or label) w, in place
        """
        self.G[i][j] = w
        self.Grev[j][i] = w

    def removeArc(self, i, j):
        """
        Delete arc i -> j in place
        """
        self.G[i].pop(j)
        self.Grev[j].pop(i)

