'''
Created on Mar 14, 2011

@author: patnaik
'''
import time
from itertools import izip
from collections import defaultdict, deque
from emr_mine import emr_all_data
from random import random

def generate_binary_vectors_froms_candidates_with_expiry(stream, candidates, class_prefix, expiry, fname):
    n = len(candidates)
    pos_count = 0; neg_count = 0; write_count = 0; p_value = 0.01
    fout = open(fname, "w")

    init = [[0] * len(episode) for episode in candidates]
    cid = [[-1] * len(episode) for episode in candidates]
    waits = defaultdict(deque)
    bag = deque()
    for alpha, candidate in enumerate(candidates):
        waits[candidate[0]].append((alpha, 0))
    
    prev_id = -1
    
    vector = [0 for _ in xrange(n)]; t_vect = [-1 for _ in xrange(n)]
    class_label = -1; t_label = -1; write_flag = False
    
    for (patient_id, med_code, _, t_day) in stream:
        if med_code.startswith(class_prefix):
            class_label = +1
            t_label = t_day
            write_flag = True
        else:
            while waits[med_code]:
                (alpha, j) = waits[med_code].pop()
                level = len(candidates[alpha])
                if j == 0:
                    init[alpha][0] = t_day
                    cid[alpha][0] = patient_id
                    bag.append((alpha, 0))
                else:
                    init[alpha][j] = init[alpha][j-1]
                    init[alpha][j-1] = 0
                    cid[alpha][j] = cid[alpha][j-1]
                    cid[alpha][j-1] = -1
                if j < level-1:
                    if candidates[alpha][j+1] == med_code:
                        bag.append((alpha, j+1))
                    else:
                        waits[candidates[alpha][j+1]].append((alpha, j+1))
                else:
                    if (expiry == None or 0 < (t_day - init[alpha][j]) < expiry) and cid[alpha][j] == patient_id:
                        vector[alpha] = 1; t_vect[alpha] = t_day; write_flag = True
                        init[alpha][j] = 0
                        for k in xrange(1, level-1):
                            init[alpha][k-1] = 0
                            try:
                                waits[candidates[alpha][k]].remove((alpha, k))
                            except ValueError:
                                pass
                            try:
                                bag.remove((alpha, k))
                            except ValueError:
                                pass
            waits[med_code].extend(bag)
            bag.clear()


        if prev_id != patient_id:
            if write_flag or random() < p_value:
                if write_flag: write_count += 1
                if class_label == 1: pos_count += 1
                else: neg_count += 1
                print >> fout, class_label,
                idx = 1
                for val, t in izip(vector, t_vect):
                    if t < t_label and val == 1:
                        print >> fout, "%d:%d" % (idx, 1),
                    else:
                        print >> fout, "%d:%d" % (idx, 0),
                    idx += 1
                print >> fout
                    
            prev_id = patient_id
            vector = [0 for _ in xrange(n)]; t_vect = [-1 for _ in xrange(n)]
            class_label = -1; t_label = -1; write_flag = False
        
    #Flush out the last record
    if write_flag or random() < p_value:
        if write_flag: write_count += 1
        if class_label == 1: pos_count += 1
        else: neg_count += 1
        print >> fout, class_label,
        idx = 1
        for val, t in izip(vector, t_vect):
            if t < t_label and val == 1:
                print >> fout, "%d:%d" % (idx, 1),
            else:
                print >> fout, "%d:%d" % (idx, 0),
            idx += 1
        print >> fout
        
    print 'Positive examples = %d' % pos_count
    print 'Negative examples = %d' % neg_count
    print 'Non-zero examples = %d' % write_count
    print 'Total = %d' % (pos_count + neg_count)



if __name__ == '__main__':
    expiry = 200
    level = 2
    #hepatitis - Cross Validation Accuracy = 66.3356%
#    class_prefix = '571'
#    candidates = (['452', '456.20'],
#                    ['456.1', '456.20'],
#                    ['456.0', '456.1'],
#                    ['452', '456.1'],
#                    ['456.1', '456.21'],
#                    ['456.0', '456.1'],
#                    ['456.1', '456.20'],
#                    ['452', '456.20'],
#                    ['452', '573.3'],
#                    ['572.8', '789.5'],
#                    ['452', '456.1'],
#                    ['070.54', '456.1'],
#                    ['070.51', '070.54'],
#                    ['070.54', '456.1'])
    
    #Septicemia - Cross Validation Accuracy = 62.4548%
#Positive examples = 16232
#Negative examples = 9758
#Non-zero examples = 24568
#Total = 25990
#    class_prefix = '038' #23 episodes 2830 occurrences 
#    candidates = (
#                    ['458.9', '995.91'],
#                    ['518.81', '995.91'],
#                    ['518.4', '586'],
#                    ['V58.81', '996.62'],
#                    ['458.9', '785.52'],
#                    ['518.81', '785.52'],
#                    ['518.81', '785.59'],
#                    ['518.4', 'V58.82'],
#                    ['518.4', 'V58.89'],
#                    ['790.7', '996.62'],
#                    ['V58.82', 'V58.89'],
#                    ['518.4', 'V58.81'],
#                    ['458.9', 'V58.81'],
#                    ['458.9', 'V58.82'],
#                    ['518.4', '518.82'],
#                    ['V58.81', 'V58.89'],
#                    ['518.81', 'V58.89'],
#                    ['518.4', '518.81'],
#                    ['518.82', 'V58.89'],
#                    ['V58.81', 'V58.82'],
#                    ['518.81', '518.82'],
#                    ['V58.81', '518.81'],
#                    ['518.81', 'V58.82'],
#                  )
    
    
    # kidney disease - Cross Validation Accuracy = 89.1996%
#    Positive examples = 17352
#    Negative examples = 2101
#    Non-zero examples = 17985
#    Total = 19453

#    Positive examples = 17352
#    Negative examples = 15674
#    Non-zero examples = 17985
#    Total = 33026
# -  Cross Validation Accuracy = 53.9151%
    class_prefix = '585'# 11 episodes 1030 occurrences
    candidates = (
                    ['276.7', '586'],
                    ['586', '276.7'],
                    ['794.4', '276.7'],
                    ['276.7', '794.4'],
                    ['794.4', '996.81'],
                    ['794.4', 'V07.2'],
                    ['996.81', 'V07.2'],
                    ['V07.2', '996.81'],
                    ['V07.2', '939.9'],
                    ['V59.4', '996.81'],
                    ['V59.4', 'V07.2'],
                )
    stream = emr_all_data('../../emrdata')
    fname = "../../emr_results/all-data-lift-5/training-set-level-%d-code-%s.txt" % (level, class_prefix)
    
    t1 = time.clock()
    generate_binary_vectors_froms_candidates_with_expiry(stream, candidates, class_prefix, expiry, fname)
    t2 = time.clock()
    
    print 'Time taken = %.2f sec' % (t2 - t1)
    
    
    
    
    
    
