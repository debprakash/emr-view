'''
Created on Dec 9, 2010

@author: patnaik
'''

from collections import defaultdict
from itertools import izip
import sys
import os
import time
import json
from emr_mine import emr_all_data

    

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
                if flag: candidates.append(episode_ij)
            else: 
                break
    return candidates


class S(object):
    def __init__(self, alpha, event):
        self.alpha = alpha
        self.event = event
        self.count = 1
        self.init = 0.0
        self.pid = -1
    def __str__(self):
        return '(%d,%d)' % (self.alpha, self.event)

def get_span(s_list):
    t_min = sys.float_info.max; t_max = 0.0
    for s in s_list:
        if t_min > s.init: t_min = s.init
        if t_max < s.init: t_max = s.init
    return (t_max - t_min)
    
def count_candidates(stream, candidates, level, expiry):
    pcount = 0
    n = len(candidates)
    counts = [0 for _ in xrange(n)]
    counter = [0 for _ in xrange(n)]
    autos = [list() for _ in xrange(n)]
    span = [0.0 for _ in xrange(n)]
    waits = defaultdict(list)

    if candidates:
        for alpha, candidate in enumerate(candidates):
            for event in candidate:
                s = S(alpha, event)
                waits[event].append(s)
                autos[alpha].append(s)
        
        prev_pid = -1
        for (pid, event, med_type, t) in stream:
            if med_type == 'PX': continue
            if pid != prev_pid:
                pcount += 1
                prev_pid = pid
                #if pcount > 100: break
            for s in waits[event]:
                alpha = s.alpha
                if s.count == 1: 
                    s.count = 0
                    counter[alpha] += 1
                s.init = t
                s.pid = pid
                #Expiry check
                if counter[alpha] == level:
                    for q in autos[alpha]:
                        if (t - q.init) > expiry or (pid != q.pid):
                            counter[alpha] -= 1
                            q.count += 1
                #Update episode count
                if counter[alpha] == level:
                    # Update episode counters
                    counts[alpha] += 1
                    span[alpha] += get_span(autos[alpha])
                            
                    # Reset automaton counters
                    counter[alpha] = 0
                    for q in autos[alpha]:
                        q.count = 1
        for alpha in xrange(len(candidates)):
            if counts[alpha] > 0:
                span[alpha] /= float(counts[alpha])
                
    return counts, span, pcount


def cull_episodes(candidates, counts, span, support, n):
    fcheck = lambda i: counts[i] >= 0 and counts[i] > (n * support)
    #fcheck = lambda i: True
    frequent = [candidates[i] for i in xrange(len(candidates)) if fcheck(i)] 
    new_counts = [counts[i] for i in xrange(len(candidates)) if fcheck(i)]
    new_span = [span[i] for i in xrange(len(candidates)) if fcheck(i)]
    return frequent, new_counts, new_span


def cull_episodes_Htest(candidates, counts, span, support, n, lattice):
    fcheck = lambda i: counts[i] > n * support
    frequent = [candidates[i] for i in xrange(len(candidates)) if fcheck(i)] 
    new_counts = [counts[i] for i in xrange(len(candidates)) if fcheck(i)]
    new_span = [span[i] for i in xrange(len(candidates)) if fcheck(i)]
    return frequent, new_counts, new_span


def write_to_file(episodes_folder, level, frequent, counts, span = None):
    filename = episodes_folder + "/%d-node.txt" % level
    
    idx = 1
    while os.path.exists(filename):
        print 'File %s exists.' % filename
        filename = episodes_folder + "/%d-node-%d.txt" % (level, idx)
        print 'Trying %s' % filename
        idx += 1
    print 'Writing %d-size frequent episodes to %s' % (level, filename)
    
    fout = open(filename, "w")
    i = 0
    if span:
        for episode, count, sp in izip(frequent, counts, span):
            print >> fout, '%s:%d:%.4f' % (episode, count, sp)
            i += 1
    else:
        for episode, count in izip(frequent, counts):
            print >> fout, '%s:%d' % (episode, count)
            i += 1
    fout.close()



def mine(stream_generator, episodes_folder, frequent, settings, level):
    
    support = settings['support']
    expiry = settings['expiry']
    print 'Generating candidates for level', level + 1
    t1 = time.clock()
    candidates = generate_candidates(level, frequent)
    t2 = time.clock()
    print 'Number of %d-size candidates = %d' % (level + 1, len(candidates))
    print 'Time taken = %.2f sec' % (t2-t1)
    level += 1
    while True:
        print 'Counting %d %d-size candidate episodes...' % (len(candidates), level)
        t1 = time.clock()
        counts, span, n = count_candidates(stream_generator(), candidates, level, expiry)
        print 'Frequency threshold (%d x %f) = %f' % (n, support, n * support)
        frequent, counts, span = cull_episodes(candidates, counts, span, support, n)
        t2 = time.clock()
        print 'Time taken = %.2f sec' % (t2-t1)
        if frequent:
            write_to_file(episodes_folder, level, frequent, counts, span)
        else:
            break
        print 'Generating candidates at level', level
        t1 = time.clock()
        candidates = generate_candidates(level, frequent)
        t2 = time.clock()
        print 'Number of %d-size candidates = %d' % (level+1, len(candidates))
        print 'Time taken = %.2f sec' % (t2-t1)
        if len(candidates) > 70000:
            print 'Too many candidates. Haulting.'
            break
        level += 1
        
def load_2_size_episodes(episodes_file):
    frequent = set()
    for line in file(episodes_file):
        parts = line.split(":")
        episode = eval(parts[0])
        #count = int(parts[1])
        frequent.add(episode)
    frequent = list(frequent)
    frequent.sort()
    return frequent


def load_episodes(episodes_folder, default_settings = None, n = 0, level = -1):
    settings_file_name = episodes_folder + "/settings.txt"
    
    if not os.path.exists(episodes_folder):
        os.makedirs(episodes_folder)
    
    # Read settings
    if os.path.exists(settings_file_name):
        settings = json.load(open(settings_file_name))
        if default_settings and default_settings != settings:
            print 'Warning: Mismatch between old settings and new settings.'
            print json.dumps(settings, sort_keys=True, indent=4)
            print 'Updating settings.'
    settings = default_settings
    json.dump(settings, open(settings_file_name, "w"), sort_keys=True, indent=4)
    
    frequent = [];
    if level == -1:
        for filename in os.listdir(episodes_folder):
            if filename.endswith("-node.txt"):
                level = max(level, int(filename.split('-')[0]))
    
    # Load episodes
    support_th = settings['support']
    if level != -1:
        episodes_file = "%s/%d-node.txt" % (episodes_folder, level)
        frequent_set = set()
        line_count = 0
        for line in file(episodes_file):
            parts = line.split(":")
            episode = eval(parts[0])
            count = int(parts[1])
            if count >= support_th * n: #default is pass-through
                frequent_set.add(frozenset(episode))
            line_count += 1
        print "Lines read:", line_count
        for episode in frequent_set:
            lepisode = list(episode)
            lepisode.sort()
            frequent.append(tuple(lepisode))
        frequent_set = None
        frequent.sort()
        print "Parallel episodes loaded: ", len(frequent)
        
        
    return frequent, level, settings

if __name__ == '__main__':
    #stream_file = '../../emrdata/Pts_1_to_150000.txt.cleaned'
    #episodes_folder = "../../emr_results/Pts_1_to_150000"
    #n = ?

    stream_generator = lambda: emr_all_data('../../emrdata')
    #episodes_folder = "../../emr_results/all-data-lift-10"
    episodes_folder = "../../emr_results/all-data-lift-2"
    n = 1620552 #1.6 million

    settings = {    'expiry'  : 200, #in days (see episode_miner)
                    'support' : 0.0001
                }
    
    print 'Loading episodes from:', episodes_folder
    frequent, level, settings = load_episodes(episodes_folder, settings, n)
    print 'Loaded %d-size episodes: %d' % (level, len(frequent))
    
    
    print 'Mining parallel episodes'
    ts1 = time.clock()
    mine(stream_generator, episodes_folder, frequent, settings, level)
    ts2 = time.clock()
    
    print 'Done.'
    print 'Total mining time = %.2f sec' % (ts2 - ts1)



