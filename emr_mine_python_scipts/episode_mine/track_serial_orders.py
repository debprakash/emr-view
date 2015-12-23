'''
Created on Feb 7, 2011

@author: patnaik
'''

import sys
import time
from collections import defaultdict
from parallel_episode_mine import load_episodes
from itertools import izip
from numpy import diff
from math import sqrt

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

def nest_advanced(autos):
    qlist = [(q.init, q.event) for q in autos]
    qlist.sort()
    flist = []; eps_list = [qlist[0]]
    flist.append(eps_list)
    for i in xrange(1, len(qlist)):
        if eps_list[-1][0] == qlist[i][0]:
            eps_list.append(qlist[i])
        else:
            eps_list = [qlist[i]]
            flist.append(eps_list)
    qtuple = []
    for eps_list in flist:
        if len(eps_list) > 1:
            temp_list = [rec[1] for rec in eps_list]
            temp_list.sort()
            qtuple.append(tuple(temp_list))
        else:
            qtuple.append(eps_list[0][1])
            
    qtuple = tuple(qtuple)
    
    return qtuple, None

def nest_simple(autos):
    qlist = [(q.init, q.event) for q in autos]
    qlist.sort()
    #qtuple = tuple([event for (_, event) in qlist])
    ttuple, qtuple = zip(*qlist)
    t_ivl = tuple(diff(ttuple))
    return qtuple, t_ivl

nest = nest_simple

def track_candidates(stream, candidates, level, expiry):
    pcount = 0
    n = len(candidates)
    counts = [0 for _ in xrange(n)]
    counter = [0 for _ in xrange(n)]
    autos = [list() for _ in xrange(n)]
    span = [0.0 for _ in xrange(n)]
    order = [defaultdict(int) for _ in xrange(n)]
    waits = defaultdict(list)
    t_ivl_s = [defaultdict(lambda: [0.0] * (level-1)) for _ in xrange(n)]
    t_ivl_ss = [defaultdict(lambda: [0.0] * (level-1)) for _ in xrange(n)]

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
                        #print expiry, t, q.init, pid, q.pid, event
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
                    qtuple, t_ivl = nest(autos[alpha])
                    vect_s = t_ivl_s[alpha][qtuple]
                    vect_ss = t_ivl_ss[alpha][qtuple]
                    for i in xrange(len(t_ivl)):
                        vect_s[i] = vect_s[i] + t_ivl[i]
                        vect_ss[i] = vect_ss[i] + (t_ivl[i] * t_ivl[i]) 
                    order[alpha][qtuple] += 1
                    for q in autos[alpha]:
                        q.count = 1
        for alpha in xrange(len(candidates)):
            if counts[alpha] > 0:
                span[alpha] /= float(counts[alpha])
                
    return counts, span, pcount, order, t_ivl_s, t_ivl_ss

from emr_mine import emr_all_data 
if __name__ == "__main__":
#    stream_file = '../../emrdata/Pts_1_to_150000.txt.cleaned'
#    episodes_folder = "../../emr_results/Pts_1_to_150000"
    levels = [7]# [3, 4, 5, 6, 7]
    stream_generator = lambda: emr_all_data('../../emrdata')
    #episodes_folder = "../../emr_results/all-data-lift-10"
    episodes_folder = "../../emr_results/all-data-lift-5"
    n = 1620552 #1.6 million

    settings = {    'expiry'  : 200, #in days (see episode_miner)
                    'support' : 0.0001
                }
    
    i = 0
    
    for level in levels:
        
        print 'Loading episodes from:', episodes_folder
        frequent, level, settings = load_episodes(episodes_folder, settings, n, level)
        expiry = settings['expiry']
        support = settings['support']
        print 'Loaded %d-size episodes: %d' % (level, len(frequent))
        
        print 'Counting %d %d-size candidate episodes...' % (len(frequent), level)
        t1 = time.clock()
        counts, spans, n_new, order, t_ivl_s, t_ivl_ss = track_candidates(stream_generator(), frequent, level, expiry)
        t2 = time.clock()
        print 'Time taken = %.2f sec' % (t2-t1)
        print 'n = %d, n_new = %d' % (n, n_new)
        
        fepisodes = episodes_folder + "/emr-episode-set-%d.txt" % level
        fout = open(fepisodes, "w")
        if level == levels[0]:
            print >> fout, "#Parallel episodes mined with support = %.4f and expiry constraint = %d days." % (settings['support'], settings['expiry'])
            print >> fout, "#Tot. no. of patients rec. sequences = %d." % n
        

        print 'Writing partial-orders data to file:', fepisodes
        for episode, count, span, serial_map, map_s, map_ss in izip(frequent, counts, spans, order, t_ivl_s, t_ivl_ss):
            print >> fout, "%d,%d,%d" % (i+1, len(serial_map), count)
            print >> fout, "|".join(episode)
            #print episode, count, span
            serial_episodes = serial_map.items()
            serial_episodes.sort(key=lambda rec: rec[1], reverse=True)
            cum_sum = 0; flag = 1
            for serial_episode, serial_count in serial_episodes:
                vect_s = map_s[serial_episode]
                vect_ss = map_ss[serial_episode]
                mean_vect = []; sd_vect = []
                for ls, ss in izip(vect_s, vect_ss):
                    mean_t = float(ls)/float(serial_count)
                    mean_vect.append("%.2f" % mean_t)
                    try:
                        sd_vect.append("%.2f" % (sqrt(float(ss - mean_t**2)/float(serial_count))))
                    except Exception, e:
                        print "ls = %f, ss = %f, serial_count = %d" % (ls, ss, serial_count)
                        print "vect_s =", vect_s
                        print "vect_ss =", vect_ss
                        raise e
                        
                str_mean_vect = "|".join(mean_vect)
                str_sd_vect = "|".join(sd_vect)
                str_serial_episode = "|".join(serial_episode)
                print >> fout, "%s:%d:%d:%s:%s" % (str_serial_episode, serial_count, flag, str_mean_vect, str_sd_vect)
                cum_sum += serial_count
                if cum_sum >= 0.75 * count: flag = 0
            i += 1
            print "###", cum_sum, count, cum_sum == count

        fout.close()

