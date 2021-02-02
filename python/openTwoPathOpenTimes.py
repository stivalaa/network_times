#!/usr/bin/env python
#
# File:    openTwoPathOpenTimes.py
# Author:  Alex Stivala
# Created: March 2019
#
# Compute list of times of arcs forming open two-paths (that are also
# not subsequently closed) in directed network with arcs as
# time-stamped events counting only two-paths where the arcs are in
# increasing time order along the direction of the two-paths.
#
# Usage: openTwoPathOpenTimes.py [-v] < input.csv > output.txt
#
# input.csv is a CSV file with no header. Each row has three fields:
# source node, destination node, timestamp
# source and destination nodes are integers (it is assumed they are
# numbered contiguously 0 .. N-1 and the number of nodes N is just
# assumed to be the maximum source or destination node number in the input)
# and timestamp is any numeric value but must be sorted ascending.
#
# Output to stdout is just one number per line, each number being
# a time that a remaining open two-path was formed.
#
# If the -v option is specified then verbose (debug) output is also
# generated to stdout.
#
# Example:
#  sort  -t, -k3,3n exampleinput_notsorted.txt  | ./openTwoPathOpenTimes.py > output.txt
# 

import csv
import sys
import getopt

from Digraph import Digraph


# Format of data is list of (sender, receiver, timestamp) tuples.
TSENDER    = 0
TRECEIVER  = 1
TTIME      = 2


def twoPaths(G, i, j):
    """
    Return a list of nodes identifying the two-paths that would be formed
    (whether open or already closed) by the addition of arc i -> j

    Parameters:
         G - digraph
         i - source of arc to test
         j - destination of arc to test

    Return value:
        Tuple of two lists ([u], [v]) where [u] is list of nodes where i -> j
        forms a new two-path u -> i -> j and [v] is list of node where i -> j
        forms a new two-path i -> j -> v.
    """
    ulist = []
    vlist = []
    for u in G.inIterator(i):
        assert(G.isArc(u, i))
        if u == i or u == j:
            continue
        ulist.append(u)
    for v in G.outIterator(j):
        assert(G.isArc(j, v))
        if v == i or v == j:
            continue
        vlist.append(v)        
    return (ulist, vlist)


def openTwoPaths(G, i, j):
    """
    Return a list of nodes identifying the open (not transitively
    closed) two-paths that would be formed by the addition of arc i -> j

    Parameters:
         G - digraph
         i - source of arc to test
         j - destination of arc to test

    Return value:
        Tuple of two lists ([u], [v]) where [u] is list of nodes where i -> j
        forms a new two-path u -> i -> j and [v] is list of node where i -> j
        forms a new two-path i -> j -> v.

    """
    ulist = []
    vlist = []
    for u in G.inIterator(i):
        assert(G.isArc(u, i))
        if u == i or u == j:
            continue
        if not G.isArc(u, j): # exclude if u->i->j transitively closed by u->j
            ulist.append(u)
    for v in G.outIterator(j):
        assert(G.isArc(j, v))
        if v == i or v == j:
            continue
        if not G.isArc(i, v): # exclude if i->j->v transitiveyl closed by i->v
            vlist.append(v)        
    return (ulist, vlist)



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


def openTwoPathOpenTimes(numNodes, transaction_list, verbose):
    """Given a list of transactions which are in the form of 
    a list of (sender, receiver, timestamp) tuples, return the list
    of times at open two-paths are created.
    
    Parameters:
        numNodes         - number of actors (nodes)
        transaction_list - list of (sender, receiver, timestamp) tuples.
                           Sender and receiver are intergers in 0..numNodes-1
                           and timestamps are numeric values.
                           The list must be ordered by timestamp ascending.
        verbose          - if True write debug output to stdout

    Return value: 
        dict { (i, j, k) : t } where (i, j, k) is an open
        directed two-path (note this means it is not part of a
        transitive triad i.e. i -> k is not present, but it may be
        part of a cyclic triad i.e. k -> i may be present), and t is
        the time the two-path was created (open). BUT only if the
        second arc in two-path has higher timestamp than the first
        (i.e. we don't count a two-path that goes backward in time
        along the path)

    """
    G = Digraph(numNodes)
    lastTime = None
    pathdict = {}  # dict mapping (i,j,k) two-path tuple to open time
    for trans in transaction_list:
        assert(trans[TSENDER] >= 0 and trans[TSENDER] < numNodes)
        assert(trans[TRECEIVER] >= 0 and trans[TRECEIVER] < numNodes)
        assert(lastTime is None or trans[TTIME] >= lastTime)
        if verbose:
            print trans[TSENDER], '->', trans[TRECEIVER], ' at time ', trans[TTIME],
        (ulist, vlist) = openTwoPaths(G, trans[TSENDER], trans[TRECEIVER])
        i = trans[TSENDER]
        j = trans[TRECEIVER]
        if len(ulist) > 0 or len(vlist) > 0:
            if verbose:
                print 'opened', len(ulist)+len(vlist), 'two-paths'
            for u in ulist:  # u -> i -> j
                path_1st_time = G.G[u][i]
                path_2nd_time = trans[TTIME] # will be G.G[i][j] when inserted
                if path_2nd_time > path_1st_time:
                    if verbose:
                        print '  path from', u, 'is forward in time (', path_1st_time, ',', path_2nd_time, '), including'
                    if not pathdict.has_key((u, i, j)):
                        pathdict[(u, i, j)] = path_2nd_time
                    else:
                        if verbose:
                            print '  two-path ' ,u, i, j, 'already present from time', pathdict[(u, i, j)], ' not updating'
                else:
                    if verbose:
                        print '  path from', u, 'is backwards in time (', path_1st_time, ',', path_2nd_time, '), skipping'
            if len(vlist) > 0:
                if verbose:
                    print '  ',len(vlist), ' are backward in time, skipping'
            for v in vlist:  #  i -> j -> v
                path_1st_time = trans[TTIME] # will be G.G[i][j] when inserted
                path_2nd_time = G.G[j][v]
                # as the transactions are ordered in time we cannot
                # have this a two-path ordered in time, as the 2nd is older
                assert(path_1st_time > path_2nd_time)
        else:
            if verbose:
                print

        # now check if the new arc i -> j would close any currently open
        # two-paths. If so, remove those from the dictionary of open
        # two paths.
        for v in closedTwoPaths(G, i, j):
            # For each v, i -> v -> j is now a two-path closed by i -> j
            if verbose:
                print '  removing ', i, v, j, ' as it is now a transitive triad'
            # note (i, v, j) might exist in pathdict as it was an open two-path
            # but NOT NECESSARILY as it might have been ignored as backward in time
            if pathdict.has_key((i, v, j)):
                pathdict.pop((i, v, j))
            else:
                if verbose:
                    print '  (did not exist in dict)'

        # add this new arc i -> j to the graph
        # note there is a potential inconsistency here in that this
        # arc might already exist in which case we update the time with
        # the new (later) time, however in the pathdict dictionary
        # we do not update times of open two-paths but keep the first
        # opening time. Need to decide which one really is correct.
        G.insertArc(trans[TSENDER], trans[TRECEIVER], trans[TTIME])

        lastTime = trans[TTIME]
    return pathdict
        
    

    
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
    openpathdict = openTwoPathOpenTimes(numNodes, transactions, verbose)
    if verbose:
        sys.stdout.write("\n".join([str(t) for t in openpathdict.iteritems()]))
        sys.stdout.write("\n")
        print 'Start output:'
    sys.stdout.write("\n".join([str(t) for t in openpathdict.itervalues()]))    
    sys.stdout.write("\n")
    
    

if __name__ == "__main__":
    main()

