#!/usr/bin/env python
#
# File:    lastCyclicClosureTime.py
# Author:  Alex Stivala
# Created: June 2020
#
# Compute time distribution of arcs forming closing
# open two-paths in directed network with arcs as time-stamped events
# counting only two-paths where the arcs are in increasing time
# order along the direction of the two-paths.
#
# This version (as opposed to the original cyclicClosureTime.py
# from March 2019 in Lugano) only considers, for each arc, a single
# two-path closure (not all the potentially multiple two-paths it
# closes): specifically, the one that is closest in time. "Closest in
# time" it taken to mean that where the second arc in the directed two-path
# (which already must have higher timestamp than the first) has the
# highest timestamp among those considered.
#
# Usage: lastCyclicClosureTime.py [-v] < input.csv > output.txt
#
# input.csv is a CSV file with no header. Each row has three fields:
# source node, destination node, timestamp
# source and destination nodes are integers (it is assumed they are
# numbered contiguously 0 .. N-1 and the number of nodes N is just
# assumed to be the maximum source or destination node number in the input)
# and timestamp is any numeric value but must be sorted ascending.
#
# Output to stdout is header line followed by one line for each
# cyclic closure processed, with opening time (timestamp from input)
# and time to closure (difference between closing arc timestamp and the
# opening timestamp).
#
# If the -v option is specified then verbose (debug) output is also
# generated to stdout.
#
# Example:
#  sort  -t, -k3,3n exampleinput_notsorted.txt  | ./cyclicClosureTime.py > output.txt
# 

import csv
import sys
import getopt

from Digraph import Digraph


# Format of data is list of (sender, receiver, timestamp) tuples.
TSENDER    = 0
TRECEIVER  = 1
TTIME      = 2


def cyclicClosedTwoPaths(G, i, j):
    """
    Return a list of nodes identifying the open two-paths that would
    be closed into a directed cycle by the addition of arc i -> j

    Parameters:
         G - digraph
         i - source of arc to test
         j - destination of arc to test

    Return value:
         List of nodes v for which the arc i -> j 
         closes the two-path j -> v -> i into a directed cycle
    """
    nodelist = []
    for v in G.inIterator(i):
        assert(G.isArc(v, i))
        if v == i or v == j:
            continue
        if G.isArc(j, v):
            nodelist.append(v) # i->j closes 2-path j->v->i into a cycle
    return nodelist



def lastCyclicClosureTime(numNodes, transaction_list, verbose):
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
        List of tuples (open_time, delta_time)
        where open_time is second timestamp in open two-path and
        and delta_time is it took open two-paths to be closed (the difference
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
        closed_2paths_v = cyclicClosedTwoPaths(G, trans[TSENDER], trans[TRECEIVER])
        if len(closed_2paths_v) > 0:
            if verbose:
                print  'closed', len(closed_2paths_v), 'two-paths via', closed_2paths_v
            path_2nd_time_list = []
            for v in closed_2paths_v:
                path_1st_time = G.G[trans[TRECEIVER]][v]     # j -> v
                path_2nd_time = G.G[v][trans[TSENDER]]       # v -> i
                if path_2nd_time > path_1st_time:
                    if verbose:
                        print '  path via', v, 'is forward in time (', path_1st_time, ',', path_2nd_time, '), considering'
                    path_2nd_time_list.append(path_2nd_time)
                else:
                    if verbose:
                        print '  path via', v, 'is backwards in time (', path_1st_time, ',', path_2nd_time, '), skipping'
            if len(path_2nd_time_list) > 0:
                path_2nd_time_max = max(path_2nd_time_list)
                delta_time = trans[TTIME] - path_2nd_time_max
                if verbose:
                    print '  ',len(path_2nd_time_list), 'paths considered as forward in time, max 2nd time is',path_2nd_time_max,' appending delta_time =', delta_time
                delta_time_list.append( (path_2nd_time_max, delta_time) )
            else:
                if verbose:
                    print '  (no paths forward in time)'
        else:
            if verbose:
                print
        if not G.isArc(trans[TSENDER], trans[TRECEIVER]):
            # only insert arc if not already one there, to keep first
            # time on transactions, not subsequent times.
            G.insertArc(trans[TSENDER], trans[TRECEIVER], trans[TTIME])
        lastTime = trans[TTIME]
    return delta_time_list
        
    

def run_example():
    """
    Run with example data from issue_1.pdf
    """
    numNodes = 6
    example_trans = [
        (1,2,1),
        (2,4,2),
        (2,3,3),
        (2,4,4),
        (1,4,5),
        (5,1,6),
        (4,1,7),
        (1,3,8),
        (5,3,9),
        (2,1,10)
    ]
    close_times = lastCyclicClosureTime(numNodes, example_trans, verbose=True)
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
    sys.stdout.write('open_timestamp cyclic_close_delta_time\n')
    time_tuples = lastCyclicClosureTime(numNodes, transactions, verbose)
    sys.stdout.write("\n".join([str(t[0]) + ' ' + str(t[1])
                                for t in time_tuples]))
    sys.stdout.write("\n")
    
    

if __name__ == "__main__":
    main()

