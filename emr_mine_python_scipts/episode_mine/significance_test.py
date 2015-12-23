'''
Created on Feb 12, 2011

@author: patnaik
'''

import time

from scipy.misc.common import comb
#from gmpy import comb

def F1(k_n, n1, n2, N):
    num = 0.0; den = 0.0
    for k in xrange(max(0, (n1+n2) - N), min(n1, n2) + 1):
        c_k = comb(N, k) * comb(N-k, n1-k) * comb(N-n1, n2-k)
        if k >= k_n: num += c_k
        den += c_k
    print 'F1', num, den
    return num/den

def F2(k_n, n1, n2, N):
    num = 0.0; den = float(comb(N, n1) * comb(N, n2))
    for k in xrange(k_n, min(n1, n2) + 1):
        num += comb(N, k) * comb(N-k, n1-k) * comb(N-n1, n2-k)
    print 'F2', num, den
    return num/den


def F3(k_n, n1, n2, N):
    den = float(comb(N, n1) * comb(N, n2))
    num = 0.0
    for k in xrange(0, k_n):
        num += comb(N, k) * comb(N-k, n1-k) * comb(N-n1, n2-k)
    print 'F3', den - num, den
    return 1 - num/den


def testf(f, fname, k_n, n1, n2, N):
    t1 = time.clock()
    for _ in xrange(1):
        val = f(k, n1, n2, N)
    t2 = time.clock()
    print '%s: Time taken = %.4f sec\t' % (fname, t2 - t1), 
    print '%s: value = %g' % (fname, val)
    

if __name__ == "__main__1":
    n1 = 200; n2 = 250; k = 1; N = n1 + n2
    testf(F1, 'F1', k, n1, n2, N)
    testf(F2, 'F2', k, n1, n2, N)
    testf(F3, 'F3', k, n1, n2, N) #Very unstable
    






''' Trying out MaxEntropy models '''

from scipy import maxentropy
from math import log

ref_pattern = None

def incexc(n, bag, count):
    pattern = [(n >> y) & 1 for y in range(count-1, -1, -1)]
    pos = []; count = 0; size = len(pattern) - sum(pattern)
    for i in xrange(len(pattern)):
        if pattern[i] == 0: pos.append(i)

    for i in xrange(2 ** size):
        new_pattern = list(pattern)
        for j in xrange(size):
            if i & (1 << j) > 0: new_pattern[pos[j]] = 1
        
        new_events = []
        for j in xrange(len(new_pattern)):
            if new_pattern[j] == 1:
                new_events.append(j)
        
        new_events = tuple(new_events)
        sign = (-1) ** (sum(new_pattern) - sum(pattern))
        #print sign, new_events
        if (ref_pattern):
            count += sign * bag[tuple([ref_pattern[idx] for idx in new_events])]
        else:
            count += sign * bag[new_events]
    return count
    

def log2(p):
    if p == 0.0: return 0
    return log(p, 2)


from itertools import combinations
from collections import defaultdict

def generate_factors(size):
    factors = []
    items = range(size)
    factor_list = []
    for i in range(1,size):
        factor_list.extend(combinations(items, i))
    #print factor_list
    factor_map = defaultdict(list)
    for x in xrange(2**size):
        for indices in factor_list:
            if all([x & (1<<i) > 0 for i in indices]):
                factor_map[indices].append(x)
    
    for indices in factor_list:
        #print indices, factor_map[indices]
        fun_str = "lambda i: i in set(%s)" % factor_map[indices]
        #print fun_str
        factors.append(eval(fun_str))
    return factors

if __name__ == "__main__1":
    generate_factors(3)
    
    
def significance_test(size, bag, samplespace, factors, E_k):
    tt = [incexc(i, bag, size) for i in samplespace]
    if any([count < 0 for count in tt]):
        raise Exception("Value Error: -ve %s" % tt)
        
    n = float(bag[()])
    q_ref = [v/n for v in tt]
    K = E_k(q_ref)
    
    model = maxentropy.model(factors, samplespace)
    model.fit(K, algorithm="CG") #  The algorithm can be 'CG', 'BFGS', 'LBFGSB', 'Powell', or 'Nelder-Mead'.
    
    p = model.probdist()
    KLdiv = sum([ p_i * (log2(p_i) - log2(q_i))   for p_i, q_i in zip(q_ref, p)])
    
    return (KLdiv, p[-1], q_ref[-1])
    
if __name__ == "__main__1":
    size = 3
    factors = generate_factors(3)
    E_k  = lambda q: [sum([q[j] for j in xrange(len(q)) if factors[i](j)])  for i in xrange(len(factors))]
    samplespace = range(2**size)

    
    bag = {():1000, (0,):100, (1,):100, (2,): 100, (0,1):50, (0,2):50, (1,2):50, (0,1,2):0}
    
    
    for val in xrange(0, 51, 5):
        bag[(0,1,2)] = val
        (KLdiv, p_maxent, p_ref) = significance_test(size, bag, samplespace, factors, E_k)
        print "%d\t%.4f\t%.4f\t%.4f" % (val, p_ref, p_maxent, KLdiv)
    
    
if __name__ == "__main__1":
#    f_A  = lambda i: i in (4,5,6,7)
#    f_B  = lambda i: i in (2,3,6,7)
#    f_C  = lambda i: i in (1,3,5,7)
#    f_AB = lambda i: i in (6,7)
#    f_AC = lambda i: i in (5,7)
#    f_BC = lambda i: i in (3,7)
#    factors = [f_A, f_B, f_C, f_AB, f_AC, f_BC]
    factors = generate_factors(3)
    E_k  = lambda q: [sum([q[j] for j in xrange(len(q)) if factors[i](j)])  for i in xrange(len(factors))]

    debug = False
    size = 3
    samplespace = range(2**size)
    #rows = [(0,0,0), (0,0,1), (0,1,0), (0,1,1), (1,0,0), (1,0,1), (1,1,0), (1,1,1)]
    
    bag = {():1000, (0,):100, (1,):100, (2,): 100, (0,1):50, (0,2):50, (1,2):50, (0,1,2):0}


    for val in xrange(0, 51, 5):
        bag[(0,1,2)] = val
        tt = [incexc(i, bag, size) for i in samplespace]
        if any([count < 0 for count in tt]):
            print val, '-ve'
            continue
        
        if debug:
            for pattern, count in zip(samplespace, tt):
                print pattern, count
    
        den = float(bag[()])#float(sum(tt))
        q_ref = [v/den for v in tt]
            
        
        K = E_k(q_ref)
        model = maxentropy.model(factors, samplespace)
        
        t1 = time.clock()
        model.fit(K, algorithm="CG") #  The algorithm can be 'CG', 'BFGS', 'LBFGSB', 'Powell', or 'Nelder-Mead'.
        t2 = time.clock()
        if debug:
            print "Training time = %.4f sec" % (t2 - t1)
            print "\nFitted model parameters are:\n" + str(model.params)
        
        p = model.probdist()
        K_fit = E_k(p)
        KLdiv = sum([ p_i * (log2(p_i) - log2(q_i))   for p_i, q_i in zip(q_ref, p)])
        
        if debug:
            print "Comparison of distribution:  fit (ref)"
            for i in samplespace:
                print "P[%d] = %.4f (%4f)" % (i, p[i], q_ref[i])
            print "KL Div = %.6f" % KLdiv
            print "Ref factor expectations: [%s]" % " ".join(map(lambda x: "%.4f" % x, K))
            print "Fit factor expectations: [%s]" % " ".join(map(lambda x: "%.4f" % x, K_fit))
        
        print "%d\t%.4f\t%.4f\t%.4f" % (val, q_ref[-1], p[-1], KLdiv)
        
        
        
''' Computing significance of all parallel episodes in the mix '''
if __name__ == "__main__1":
    
    lattice = {}
    n = 1620552
    lattice[()] = n

    path = "../../emr_results/all-data-lift-5"
    print 'Loading the lattice of frequent episodes'
    file_significance = path + "/significance.txt"
    fout = open(file_significance, 'w')
    rec_count = 0; tot_count = 0
    t1 = time.clock()
    for level in [1,2,3,4,5,6,7]:
        if (level >= 3):
            factors = generate_factors(level)
            E_k  = lambda q: [sum([q[j] for j in xrange(len(q)) if factors[i](j)])  for i in xrange(len(factors))]
            samplespace = range(2**level)
        
        episodes_file = path + "/%d-node.txt" % level
        print 'File:', episodes_file
        for line in file(episodes_file):
            parts = line.split(":")
            if level == 1: #TODO: Fix me
                episode = (parts[0],)
            else:
                episode = eval(parts[0])
            count = int(parts[1])
            lattice[episode] = count
        
            if level >= 3:
                ref_pattern = episode
                try:
                    (KLdiv, p_maxent, p_ref) = significance_test(level, lattice, samplespace, factors, E_k)
                    print >> fout, "%s:%g:%g:%g" % (ref_pattern, p_ref, p_maxent, KLdiv)
                    rec_count += 1
                except KeyError, e:
                    print episode, ' key error: ', e
                except Exception, e:
                    print e
                tot_count += 1
    fout.close()
    t2 = time.clock()
    print 'Time taken = %.2f sec' % (t2 - t1)
    print 'Number of records written = %d (of %d)' % (rec_count, tot_count)
    
    
    
        
''' Fixing 2-node counts '''
from parallel_episode_mine import count_candidates
from emr_mine import emr_all_data
from itertools import izip

if __name__ == "__main__1":
    print ''' Fixing 2-node counts '''
    t1 = time.clock()
    level = 2; expiry = 200; candidates = []
    path = "../../emr_results/all-data-lift-5"
    stream = emr_all_data('../../emrdata')
    
    episodes_file = path + "/%d-node.txt" % level
    print 'File:', episodes_file
    for line in file(episodes_file):
        parts = line.split(":")
        episode = eval(parts[0])
        candidates.append(episode)
        
    counts, spans, n = count_candidates(stream, candidates, level, expiry)
    
    episodes_file = path + "/%d-node-new.txt" % level
    fout = open(episodes_file, 'w')
    for episode, count, span in izip(candidates, counts, spans):
        print >> fout, '%s:%d:%.4f' % (episode, count, span)
    fout.close()
    t2 = time.clock()
    
    print 'Time taken = %.2f sec' % (t2 - t1)
    
    



if __name__ == "__main__":
    path = "../../emr_results/all-data-lift-5"
    file_significance = path + "/significance.txt"

    t1 = time.clock()
    print 'Load the map'
    sig_map = {}
    for line in file(file_significance):
        parts = line.split(":")
        episode, p_ref, p_maxent, KLdiv = [eval(parts[0])] +  map(float, parts[1:])
        sig_map[episode] = (p_ref, p_maxent, KLdiv)
    
    for level in [4,5,6,7]:#[3]:
        print 'Reading the entire set of display partial orders (level = %d)' % level
        global_list = []
        fname = path + "/emr-episode-set-%d.txt" % level
        fin = open(fname)
        begin_id = -1
        while True:
            line = fin.readline()
            if line:
                if line.startswith("#"): continue
                (id, n, count) = map(int, line.split(","))
                if begin_id == -1: begin_id = id
                #print (id, n, count) 
                line = fin.readline().strip()
                episode = tuple(line.split(r"|"))
                serial_episodes = [ fin.readline().strip() for i in xrange(n)]
                if episode in sig_map:
                    (p_ref, p_maxent, KLdiv) = sig_map[episode]
                else:
                    (p_ref, p_maxent, KLdiv) = (0,0,0)
                global_list.append((id, n, count, episode, p_ref, p_maxent, KLdiv, serial_episodes))
            else:
                break

        print 'Reordering the list'
        global_list.sort(key=lambda rec: rec[6], reverse=True)
    
    
        print 'Rewriting the list'
        fname = path + "/emr-episode-orderedset-%d.txt" % level
        fout = open(fname, 'w')
        for (id, n, count, episode, p_ref, p_maxent, KLdiv, serial_episodes) in  global_list:
            print >> fout, "%d,%d,%d,%g,%g,%g" % (begin_id, n, count, p_ref, p_maxent, KLdiv)
            print >> fout, "|".join(episode)
            for line in serial_episodes:
                print >> fout, line
            begin_id += 1
    t2 = time.clock()
    print 'Time taken = %.2f sec' % (t2 - t1)
    
    
    
    
    