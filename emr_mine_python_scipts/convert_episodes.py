'''
Created on Jan 25, 2011

@author: patnaik
'''

import time
from collections import defaultdict


if __name__ == "__main__":
    t1 = time.clock() 
    filename = '../emr_results/dumpfile-0.001-oi-20000.txt'
    pq_map = defaultdict(list)
    for line in file(filename):
        try:
            if line.startswith("Episode") or line.startswith("----") or line.startswith("No."): continue
            parts = line.split(":")
            eps = parts[0].split("-")
            episode = [eps[i].strip() for i in xrange(0,len(eps),2)]
            count = int(parts[1])
    
            if len(episode) < 2: continue        
            if len(episode) != len(set(episode)): continue
            
            episode_key = episode[:]
            episode_key.sort()
            episode_key = tuple(episode_key)
            pq_map[episode_key].append((episode, count))
        except:
            pass


    episode_keys = pq_map.keys()
    episode_keys.sort()
    
    fout = open("../emr_results/emr-episode-set.txt", "w")
    for (i, episode_key) in enumerate(episode_keys):
        print >> fout, "%d,%d" % (i+1, len(pq_map[episode_key]))
        print >> fout, "|".join(episode_key)
        for serial_episode, count in pq_map[episode_key]:
            print >> fout, "%s:%d" % ("|".join(serial_episode), count)
    
    t2 = time.clock()
    print "Time taken = %.2f sec" % (t2 - t1)
    
    
    
    