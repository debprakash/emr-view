'''
Created on Dec 18, 2010

@author: patnaik
'''

from collections import defaultdict, deque
from itertools import izip
import time

def read_event(line):
    parts = line.split(',')
    event = int(parts[0])
    t = float(parts[1])
    return event, t


def binary_find(seq, search):
    left = 0; right = len(seq)
    previous_center = -1
    if search < seq[0]: return False
    while 1:
        center = (left + right) / 2
        candidate = seq[center]
        if search == candidate: return True
        if center == previous_center: return False
        elif search < candidate:
            right = center
        else:
            left = center
        previous_center = center
    

def generate_candidates(level, frequent):
    frequent.sort()
    candidates = []
    n = len(frequent)
    for i in xrange(n):
        episode_i = frequent[i]
        for j in xrange(i+1,n):
            episode_j = frequent[j]
            if episode_i[:-1] == episode_j[:-1]:
                episode_ij = episode_i + tuple([episode_j[-1]])
                flag = True
                for k in xrange(level + 1):
                    episode_k = episode_ij[:k] + episode_ij[k + 1:]
                    if not binary_find(frequent, episode_k):
                        flag = False
                        break
                if flag: 
                    candidates.append(episode_ij)

                episode_ji = episode_j + tuple([episode_i[-1]])
                flag = True
                for k in xrange(level + 1):
                    episode_k = episode_ji[:k] + episode_ji[k + 1:]
                    if not binary_find(frequent, episode_k):
                        flag = False
                        break
                if flag: 
                    candidates.append(episode_ji)
            else: 
                break
    return candidates

def count_events(stream):
    n = 0
    count_map = defaultdict(int)
    for event, T in stream:
        count_map[event] += 1
        n += 1
    
    events = count_map.keys()
    events.sort()
    
    candidates = [(event,) for event in events]
    counts = [count_map[event] for event in events]
    return candidates, counts, n, T


def count_candidates_expiry(stream, candidates, level, expiry):
    n = len(candidates)
    counts = [0 for _ in xrange(n)]

    if candidates:
        init = [[0] * level for _ in xrange(n)]
        cid = [[-1] * level for _ in xrange(n)]
        waits = defaultdict(deque)
        bag = deque()
        for alpha, candidate in enumerate(candidates):
            waits[candidate[0]].append((alpha, 0))
        
        for (patient_id, med_code, _, t_day) in stream:
            while waits[med_code]:
                (alpha, j) = waits[med_code].pop()
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
                        counts[alpha] += 1
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
    return counts





def cull_episodes(candidates, counts, support, n):
    frequent = [candidates[i] for i in xrange(len(candidates)) if counts[i] > n * support]
    new_counts = [counts[i] for i in xrange(len(candidates)) if counts[i] > n * support]
    return frequent, new_counts


def write_to_file(file_name, frequent, counts):
    fout = open(file_name, "a")
    i = 0
    for episode, count in izip(frequent, counts):
        print >> fout, '%d:%s:%d' % (i, episode, count)
        #print '%s:%d' % (episode, count)
        i += 1
    print >> fout, '-------------------------------------------'
    print '-------------------------------------------'
    fout.close()



def stream_reader(file_name):
    n = 0
    for line in file(file_name):
        event, t = read_event(line)
        yield (event, n)
        n += 1



    