'''
Created on Dec 29, 2010

@author: patnaik
'''


#def naive_common_interval(pi_AB, C_prev = None):
#    n = len(pi_AB)
#    C = set()
#    for x in xrange(n-1):
#        l = u = pi_AB[x]
#        for y in xrange(x+1, n):
#            l = min(l, pi_AB[y])
#            u = max(u, pi_AB[y])
#            if u - l - (y - x) == 0 and (C_prev == None or (l,u) in C_prev):
#                C.add((l,u))
#    return C


def naive_common_interval_order(pi_AB, pos_map, C_prev):
    n = len(pi_AB)
    C = set()
    for x in xrange(n):
        l = u = pi_AB[x]
        for y in xrange(x, n):
            l = min(l, pi_AB[y])
            u = max(u, pi_AB[y])
            if (u - l) - (y - x) == 0 and (C_prev == None or (l,u) in C_prev):
                pos_map[(l,u)].append(x)
                C.add((l,u))
    return C


from pygraph.classes.digraph import digraph
from pygraph.algorithms.critical import transitive_edges



def reducegraph(edges):
    g = digraph()
    nodes = set()
    for (x, y) in edges:
        if x not in nodes:
            nodes.add(x)
            g.add_node(x)
        if y not in nodes:
            nodes.add(y)
            g.add_node(y)
        g.add_edge((x,y))

    for (x,y) in transitive_edges(g):
        if (x,y) in edges: edges.remove((x,y))
    return edges



def make_tree(C, orders):
    node_map = dict([(tuple(C[k]), k) for k in xrange(len(C))])
    #print node_map
    nodef = lambda x: node_map[C[x]]
    edges = set()
    for i in xrange(len(C)):
        for j in xrange(len(C)):
            if i == j: continue
            if C[i][0] <= C[j][0] and C[i][1] >= C[j][1]:
                edges.add((nodef(i), nodef(j)))

    edges = reducegraph(edges)
    edges = list(edges)
    edges.sort()
    for (i, j) in edges:
        print C[i], "->", C[j]
    

def inv_map(seq_1, seq_2): #O(n)
    m = {}
    for i in xrange(len(seq_1)):
        m[seq_1[i]] = i
    return [m[x] for x in seq_2]
    

def common_intervals(sequences, pos_map):
    C = None
    for i in xrange(0,len(sequences)):
        pi_AB = inv_map(sequences[0], sequences[i])
        C = naive_common_interval_order(pi_AB, pos_map, C)
        #C = naive_common_interval(pi_AB, C)
    if C == None: C = []
    else:
        C = list(C)
        C.sort()
    return C
    
class Node(object):
    def __init__(self):
        self.parent = None
        self.value = 0
        self.type = 'L'
        self.children = []



from collections import defaultdict
if __name__ == '__main__':
    print 'Common interval'
    
    sequences = [(1,2,3,4,5,6,7,8,9), (9,8,4,5,6,7,1,2,3), (1,2,3,8,7,4,5,6,9)]
    #sequences = [(1,2,3,4,5,6), (3,1,2,4,5,6), (2,3,1,4,5,6)]
    #sequences = [(1,2,3), (2,3,1), (3,2,1)]
    #sequences = [(1,2,3,4), (2,1,3,4), (1,2,4,3), (2,1,4,3)]
    #sequences = [(1,2,3,4,5), (1,2,3,4,5)]
    
    pos_map = defaultdict(list)
    C = common_intervals(sequences, pos_map)
    for (l,u) in C:
        print "(%d,%d)" % (l, u),
        print " locations =", pos_map[(l,u)]
    
    #make_tree(C, pos_map)
    
    
    