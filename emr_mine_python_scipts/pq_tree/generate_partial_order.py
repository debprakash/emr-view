'''
Created on Dec 30, 2010

@author: patnaik
'''


from PQTree import PQTree
from common_intervals import common_intervals


def list_intervals(node):
    vect = []; leaf_list = []
    if node.hasChildren():
        for child in node.getAllChildren():
            id_list = list_intervals(child)
            vect.append(id_list)
            leaf_list.extend(id_list)
        if node.isPNode():
            vect.sort()
        return vect
    else:
        return [node.getData()]
    

#def str_node(node, ref_list):
#    vect = []
#    if node.hasChildren():
#        for child in node.getAllChildren():
#            vect.append(str_node(child, ref_list))
#        if node.isPNode():
#            vect.sort()
#            return '(%s)' % (' '.join(vect))
#        else:
#            return '(%s)' % ('->'.join(vect))
#    else:
#        return str(ref_list[node.getData()])
#    
#
#def generate_partial_order(sequences):
#    if len(sequences) == 1:
#        vect = map(str, sequences[0])
#        return '(%s)' % ('->'.join(vect))
#    n = len(sequences[0])
#    C = common_intervals(sequences)
#    T = PQTree(n)
#    for s in C:
#        T.reduction(s)
#    return str_node(T.getRoot(), sequences[0])

def normalize(ref):
    idx = ref[:]; idx.sort()
    idx_map = dict([(idx[i],i) for i in xrange(len(idx))])
    return [idx_map[x] for x in ref]


def str_node(node, ref_list, pos_map):
    vect = []
    if node.hasChildren():
        l_min = len(ref_list); u_max = 0; child_ivls = []
        for child in node.getAllChildren():
            (s, l, u) = str_node(child, ref_list, pos_map)
            child_ivls.append((l,u))
            l_min = min(l_min, l); u_max = max(u_max, u)
            vect.append(s)
        # Print locations 
        print "Node %s locations: %s" % (vect, pos_map[(l_min, u_max)]),
        print "ivls:", child_ivls
        for (l,u) in child_ivls:
            print "  %s: child locations = %s" % ((l,u), pos_map[(l,u)])
        
        node_loc = pos_map[(l_min, u_max)]
        i = 0; flag = True; ref = [pos_map[(l, u)][i] - node_loc[i] for (l,u) in child_ivls]
        print "ref:", ref
        for i in xrange(1, len(node_loc)):
            tst = [pos_map[(l, u)][i] - node_loc[i] for (l,u) in child_ivls]
            print "tst:", tst
            if ref != tst:
                flag = False
                break
        print flag
        # Format the children
        if flag:
            s_new = '(%s)' % ('->'.join([vect[i] for i in normalize(ref)]))
        else:
            vect.sort()#reverse=True
            s_new = '(%s)' % (' '.join(vect))
        print s_new
        return (s_new, l_min, u_max)
    
    else:
        l = node.getData()
        return (str(ref_list[l]), l, l)
    

from collections import defaultdict

def generate_partial_order(sequences):
    n = len(sequences[0])
    #C = common_intervals(sequences)
    pos_map = defaultdict(list)
    C = common_intervals(sequences, pos_map)
    T = PQTree(n)
    for s in C:
        T.reduction(s)
    return str_node(T.getRoot(), sequences[0], pos_map)


if __name__ == '__main__':
    
    #sequences = [(1,2,3,4,5,6,7,8,9), (9,8,4,5,6,7,1,2,3), (1,2,3,8,7,4,5,6,9)]
    #sequences = [(1,2,3,4,5,6), (3,1,2,4,5,6), (2,3,1,4,5,6)]
    #sequences = [(1,2,3,4), (2,3,4,1), (3,4,1,2), (4,1,2,3)]
    #sequences = [(1,2,3,4,5)]
    sequences = [(1,2,3),(1,3,2)]
    
    print 'For sequences:'
    for seq in sequences:
        print seq
    s, l, u = generate_partial_order(sequences)
    print
    print "Partial order:",s
    