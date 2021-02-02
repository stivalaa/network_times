#!/usr/bin/env python
#
# File:    transitiveClosureTime.py
# Author:  Alex Stivala
# Created: March 2019
#
# Compute time distribution of arcs forming closing
# open two-paths in directed network with arcs as time-stamped events
# counting only two-paths where the arcs are in increasing time
# order along the direction of the two-paths.
#
# Usage: transitiveClosureTime.py [-v] < input.csv > output.txt
#
# input.csv is a CSV file with no header. Each row has three fields:
# source node, destination node, timestamp
# source and destination nodes are integers (it is assumed they are
# numbered contiguously 0 .. N-1 and the number of nodes N is just
# assumed to be the maximum source or destination node number in the input)
# and timestamp is any numeric value but must be sorted ascending.
#
# Output to stdout is just one number per line, each number being
# a time to transitive closure.
#
# If the -v option is specified then verbose (debug) output is also
# generated to stdout.
#
# Example:
#  sort  -t, -k3,3n exampleinput_notsorted.txt  | ./transitiveClosureTime.py > output.txt
# 

import csv
import sys
import getopt

from Digraph import Digraph


# Format of data is list of (sender, receiver, timestamp) tuples.
TSENDER    = 0
TRECEIVER  = 1
TTIME      = 2



def closedTwoPaths(G, i, j):
    """
    Return a list of nodes identifying the open two-paths that would
    be closed by the addition of arc i -> j

    Parameters:
         G - digraph
         i - source of arc to test
         j - destination of arc to test

    Return value:
         List of nodes v for which the arc i -> j transitively 
         closes the two-path i -> v -> j
    """
    nodelist = []
    for v in G.outIterator(i):
        assert(G.isArc(i, v))
        if v == i or v == j:
            continue
        # Note we do NOT include the case commented out below
        # as although it is necessary when counting transitive triads
        # we do not want it here as it is not closing an existing
        # two-path with i->j but rather creating an already closed
        # two-path i->j->v where the existing arc i->v closes it.
        # if G.isArc(j, v):
        #     pass # creates transitive triangle i->j, j->v, i->v
        if G.isArc(v, j):
            nodelist.append(v) # creates transitive triangle i->v, v->j, i->j
    # Note this is tricky: when counting transitive triangles (triad
    # census 030T) we need to do the below to count if a two-path
    # v -> i -> j is closed by v -> j but note this is NOT closing
    # an existing two-path with i->j, rather it is creating such a two-path
    # which is 'already closed' by the existing v->j so we must NOT
    # include it here for this purpose.
    # for v in G.inIterator(i):
    #     assert(G.isArc(v, i))
    #     if v == i or v == j:
    #         continue
    #     if G.isArc(v, j):
    #         pass # this creates a transitive triangle i -> j, v -> i, v -> j
    return nodelist


def transitiveClosureTime(numNodes, transaction_list, verbose):
    """
    Given a list of transactions which are in the form of 
    a list of (sender, receiver, timestamp) tuples, return the list
    of times at which open two-paths are closed.
    
    Parameters:
        numNodes         - number of actors (nodes)
        transaction_list - list of (sender, receiver, timestamp) tuples.
                           Sender and receiver are intergers in 0..numNodes-1
                           and timestamps are numeric values.
                           The list must be ordered by timestamp ascending.
        verbose          - if True write debug output to stdout

    Return value:
        List of times it took open two-paths to be closed (the difference
        in timestamp between the closing transaction (arc) and the second
        (along arc) timestamp in the open two-path, BUT only if the second
        arc in two-path has higher timestamp than the first (i.e. we
        don't count a two-path that goes backward in time along the path)
    """
    G = Digraph(numNodes)
    lastTime = None
    delta_time_list = []
    for trans in transaction_list:
        assert(trans[TSENDER] >= 0 and trans[TSENDER] < numNodes)
        assert(trans[TRECEIVER] >= 0 and trans[TRECEIVER] < numNodes)
        assert(lastTime is None or trans[TTIME] >= lastTime)
        if verbose:
            print trans[TSENDER], '->', trans[TRECEIVER], ' at time ', trans[TTIME],
        closed_2paths_v = closedTwoPaths(G, trans[TSENDER], trans[TRECEIVER])
        if len(closed_2paths_v) > 0:
            if verbose:
                print  'closed', len(closed_2paths_v), 'two-paths via', closed_2paths_v
            for v in closed_2paths_v:
                path_1st_time = G.G[trans[TSENDER]][v]
                path_2nd_time = G.G[v][trans[TRECEIVER]]
                if path_2nd_time > path_1st_time:
                    if verbose:
                        print '  path via', v, 'is forward in time (', path_1st_time, ',', path_2nd_time, '), including'
                    delta_time = trans[TTIME] - path_2nd_time
                    delta_time_list.append(delta_time)
                else:
                    if verbose:
                        print '  path via', v, 'is backwards in time (', path_1st_time, ',', path_2nd_time, '), skipping'
        else:
            if verbose:
                print
        if not G.isArc(trans[TSENDER], trans[TRECEIVER]):
            # only insert arc if not already one there, to keep first
            # time on transactions, not subsequent times.
            G.insertArc(trans[TSENDER], trans[TRECEIVER], trans[TTIME])
        lastTime = trans[TTIME]
    return delta_time_list
        
    

def run_example_1():
    """
    Run with example data
    """
    numNodes = 10
    example_trans = [ (1, 2, 0),
                      (0, 1, 1),
                      (0, 3, 2),
                      (3, 2, 3),
                      (0, 2, 4),
                      (2, 1, 5)]

    close_times = transitiveClosureTime(numNodes, example_trans)
    print 'times to closure:', close_times

def run_example():
    """
    Run with example data
    """
    numNodes = 10
    example_trans = [ (0, 1, 1),
                      (1, 2, 2),
                      (0, 3, 3),
                      (3, 2, 4),
                      (0, 2, 5)]

    close_times = transitiveClosureTime(numNodes, example_trans)
    print 'times to closure:', close_times

def usage(progname):
    """
    Print usage message and exit
    """
    sys.stderr.write("usage: "  + progname + " [-v]\n"
                     "-v : verbose output\n")
    sys.exit(1)

def main():
    """
    See comments at top of file
    """
    verbose = False
    try:
        opts,args = getopt.getopt(sys.argv[1:], "v")
    except:
        usage(sys.argv[0])
    for opt,arg in opts:
        if opt == "-v":
            verbose = True
        else:
            usage(sys.argv[0])

    if len(args) != 0:
        usage(sys.argv[0])

        
    reader = csv.reader(sys.stdin)
    transactions = [(int(x[TSENDER]), int(x[TRECEIVER]), float(x[TTIME]))
                    for x in reader]
    numNodes = max([x[TSENDER] for x in transactions] +
                   [x[TRECEIVER] for x in transactions]) + 1
    if verbose:
        print 'numNodes = ', numNodes
    close_times = transitiveClosureTime(numNodes, transactions, verbose)
    sys.stdout.write("\n".join([str(t) for t in close_times]))
    sys.stdout.write("\n")
    
    

if __name__ == "__main__":
    main()

