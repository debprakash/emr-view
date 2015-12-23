'''
Created on Jan 6, 2011

@author: patnaik
'''

from collections import defaultdict
from pq_tree.generate_partial_order import generate_partial_order
from string import strip
import csv

def load_map():
    ret_map = {}
    n = 0
    map_file_name = "../emrdata/dxcodes.csv"
    filereader = csv.reader(open(map_file_name))
    
    for parts in filereader:
        code = parts[0]
        desc = parts[2][0].upper() + parts[2][1:]
        if desc[-1] == '"': desc = desc[:-1]
        desc = desc + "."
        ret_map[code] = desc
        n += 1
    print "Read %d records." % n
    return ret_map
    
def get_codes(episode_list):
    ret_set = set()
    for code in episode_list:
        if code.startswith("{"):
            codes = map(strip, code[1:-1].split(","))
            for xcode in codes:
                ret_set.add(xcode)
        else:
            ret_set.add(code)
    ret_set = list(ret_set)
    ret_set.sort()
    return ret_set

if __name__ == "__main__1":
    
    code_map = load_map()

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
            if any(map(lambda rec: rec.startswith("V"), get_codes(episode))): continue
            
            episode_key = episode[:]
            episode_key.sort()
            episode_key = tuple(episode_key)
            pq_map[episode_key].append((episode, count))
        except:
            pass
    
    fout = open("../emr_results/partial-orders-dumpfile-0.001-oi-20000-no-vaccinations-1.txt", "w")
    
    episode_keys = pq_map.keys()
    episode_keys.sort()
    
    
    for (i, episode_key) in enumerate(episode_keys):
        
        print >> fout, "%d." % (i+1)
        eps_list = pq_map[episode_key]
        print >> fout, "Codes: (%s)" % " ".join(episode_key)
        sequences = []
        print >> fout, '\tPermutation, Count'
        for episode, count in eps_list:
            print >> fout, '\t[%s], %d' % (" ".join(episode), count)
            sequences.append(episode)
        print >> fout, "Partial order:", generate_partial_order(sequences)
        print >> fout, "Definion of codes:"
        
        for code in get_codes(episode_key):
            if code in code_map:
                print >> fout, code, code_map[code]
            else:
                print >> fout, code, "NA"
        print >> fout
        print >> fout
    
    print "Done."
        



if __name__ == "__main__":
    code_map = load_map()

    code_list = set(['145.9','792.9','99243','88321'])
    for code in code_list:
        if code in code_map:
            print code, "&", code_map[code], "\\\\"

        

