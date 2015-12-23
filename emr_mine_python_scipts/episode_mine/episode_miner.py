'''
Created on Jan 3, 2011

@author: patnaik
'''
from time import clock
from collections import deque, defaultdict
from emr_mine import emr_stream_reader, emr_all_data, emr_all_data2 
from itertools import izip

from serial_episode_mine import write_to_file, cull_episodes, generate_candidates 
from serial_episode_mine import count_candidates_expiry


''' 
    Count and records stats of all possible 2-size nodes
'''
def count_two_size_episodes(stream, output_file, chunk = -1):
    t1 = clock()
    #Collect all two size patterns
    expiry_span = 500#200;
    
    prev_patient_id = 0
    buffer = []
    parallel_episodes = defaultdict(int)
    serial_episodes = defaultdict(int)
    singletons = defaultdict(int)
    n = 0
    print 'Processing data...'
    for (patient_id, med_code, med_type, t_day) in stream:

        if prev_patient_id != 0 and prev_patient_id != patient_id:
            #Process the buffer
            n += 1
            pairs_set = set()
            pairs_tuple = set()
            for med_code_A, _ in set(buffer): singletons[med_code_A] += 1
            for i in xrange(len(buffer)-1):
                med_code_A, t_A = buffer[i]
                for j in xrange(i+1, len(buffer)):
                    med_code_B, t_B = buffer[j]
                    if med_code_A == med_code_B: continue
                    if t_B - t_A > expiry_span: break
                    tup_AB = (med_code_A, med_code_B)
                    pairs_set.add(frozenset(tup_AB))
                    pairs_tuple.add(tup_AB)
            for key in pairs_set:
                parallel_episodes[key] += 1
            for key in pairs_tuple:
                serial_episodes[key] += 1
            del buffer[:]
        buffer.append((med_code, t_day))
        prev_patient_id = patient_id
    t2 = clock()
    print 'Time taken = %.2f sec' % (t2 - t1)
    print 'Processing episodes...'
    episode_list = serial_episodes.keys()
    episode_list.sort()
    
    fout = open(output_file, "w")
    for tup_AB in episode_list:
        try:
            (A,B) = tup_AB
            count_A = float(singletons[A])
            count_B = float(singletons[B])
            count_AB = float(serial_episodes[tup_AB])
            count_parallel_AB = float(parallel_episodes[frozenset(tup_AB)])
            if count_AB < 0.0001 * n: continue
            supp_A = count_A/n
            supp_B = count_B/n
            supp_AB = count_AB/n
            lift = (count_AB * n)/(count_A * count_B)
            pratio =  count_AB/count_parallel_AB
            confidence = count_AB/count_AB
            print >> fout, A, B, count_A, count_B, count_AB, count_parallel_AB, n, supp_A, supp_B, supp_AB, lift, pratio, confidence
        except Exception as e:
            print e
            print 'continuing...'
    fout.close()
    print 'done'
    print 'Total number of sequences = %d' % n
    print 'Total number of episodes = %d' % len(episode_list)
    t2 = clock()
    print 'Time taken = %.2f sec' % (t2 - t1)
        


def prune_two_size_episodes(infile, support_th, lift_th, outfile = None):
    t1 = clock()
    #First count how many are possible
    frequent_2 = []; counts_2 = []; frequent_1_map = {}
    rec_count = 0; tot_count = 0
    if outfile: fout = open(outfile, "w")
    for line in file(infile):
        parts = line.split()
        A, B = parts[:2]
        #print parts[2:7]
        count_A, count_B, count_AB, count_parallel_AB, n = map(float, parts[2:7])
        supp_A, supp_B, supp_AB, lift, pratio, confidence = map(float, parts[7:])
        if supp_AB >= support_th and lift > lift_th and count_AB > 1:
            rec_count += 1
            frequent_2.append((A,B))
            counts_2.append(count_AB)
            if A not in frequent_1_map: 
                frequent_1_map[A] = count_A
            elif frequent_1_map[A] != count_A:
                print 'Inconsistency: ', A, B, frequent_1_map[A], count_A
            
            if B not in frequent_1_map: 
                frequent_1_map[B] = count_B
            elif frequent_1_map[B] != count_B:
                print 'Inconsistency: ', A, B, frequent_1_map[B], count_B

            if outfile:
                print >> fout, A, B, count_A, count_B, count_AB, count_parallel_AB, n,\
                        supp_A, supp_B, supp_AB, lift, pratio, confidence
        tot_count += 1 
#        if count_AB != count_parallel_AB:
#            print (A,B), set((A,B)), count_AB, count_parallel_AB
#            break
    t2 = clock()
    print 'Time taken = %.2f sec' % (t2 - t1)
    print 'Fraction of 2-node episodes found useful = (%d/%d) = %f' % (rec_count, tot_count, float(rec_count)/float(tot_count))
    if outfile: fout.close()
    return frequent_2, counts_2, frequent_1_map
    
        

def write_episodes_to_file(file_name, frequent, counts):
    fout = open(file_name, "w")
    for episode, count in izip(frequent, counts):
        print >> fout, "%s:%d" % (episode, count)
    fout.close()

def read_episodes_from_file(file_name):
    frequent = []
    count = []
    for line in file(file_name):
        parts = line.split(":")
        episode = eval(parts[0])
        count = int(parts[1])
        frequent.append(episode)
        counts.append(count)
    return frequent, count


import os
import json

''' Combining all 2-node episodes from all the chucnks '''
if __name__ == '__main__1':
    # Do it by parts
    flist = ['Pts_1_to_150000.txt.cleaned', 'Pts_150001_to_300000.txt.cleaned', 'Pts_300001_to_450000.txt.cleaned',\
     'Pts_450001_to_600000.txt.cleaned', 'Pts_600001_to_750000.txt.cleaned', 'Pts_750001_to_900000.txt.cleaned',\
     'Pts_900001_to_1050000.txt.cleaned', 'Pts_1050001_to_1200000.txt.cleaned', 'Pts_1200001_to_1350000.txt.cleaned',\
     'Pts_1350001_to_1500000.txt.cleaned', 'Pts_1500001_and_up.txt.cleaned']
    
    support_th = 0.0001
    lift_th = 2.0 #5.0
    expiry_span = 200 #from count_two_size_episodes

    outdir = '../../emr_results/'
    subdir = outdir + '/all-data-lift-2/'
    if not os.path.exists(subdir): os.mkdir(subdir)
    
    settings = {'support' : support_th, 'expiry': expiry_span}
    json.dump(settings, open(subdir + "settings.txt", "w"), sort_keys=True, indent=4)
    
    combined_2_node_episodes = '2-node.txt'
    combined_1_node_episodes = '1-node.txt'
    
    
    ts1 = clock()
    episodes_2_map = defaultdict(float)
    episodes_1_map = defaultdict(float)
    for fname in flist:
        print 'Processing file: ', fname
        t1 = clock()
        in_file = outdir + '2-node-%s' % fname
        out_file = subdir + '2-node-%s' % (fname[:-8] + ".filtered")
        frequent_2, counts_2, frequent_1_map = prune_two_size_episodes(in_file, support_th, lift_th, out_file)
        for episode, count in izip(frequent_2, counts_2): episodes_2_map[episode] += count
        for episode, count in frequent_1_map.iteritems(): episodes_1_map[episode] += count
        t2 = clock()
        print 'Time taken = %.2f sec' % (t2 - t1)
        print 'Read #of episodes = ', len(frequent_2)
        print 'Number of episodes =', len(episodes_2_map)
        
#        print 'Writing to file'
#        fout = open(outdir + combined_2_node_episodes, 'w')
#        for episode, count in episodes_2_map.iteritems():
#            print >> fout, '%s:%d' % (episode, count)
#        fout.close()
#        print 'done.'
#        print
    ts2 = clock()
    print 'Total time taken = %.2f sec' % (ts2 - ts1)
    print 'Total number of 2-node episodes = ', len(episodes_2_map)
    print 'Total number of 1-node episodes = ', len(episodes_1_map)
    
    # Write the 1-size episodes
    episodes = episodes_1_map.items()
    episodes.sort(key=lambda rec: rec[1], reverse=True)
    print 'Writing to file [sorted]: 1-size episodes'
    fout = open(subdir + combined_1_node_episodes, 'w')
    for episode, count in episodes:
        print >> fout, '%s:%d' % (episode, count)
    fout.close()
    print 'done.'

    # Write the 2-size episodes
    episodes = episodes_2_map.items()
    episodes.sort(key=lambda rec: rec[1], reverse=True)
    print 'Writing to file [sorted]: 2-size episodes'
    fout = open(subdir + combined_2_node_episodes, 'w')
    for episode, count in episodes:
        print >> fout, '%s:%d' % (episode, count)
    fout.close()
    print 'done.'
    
    

''' Pruning episodes '''
if __name__ == "__main__1":
    filename = '../../emr_results/2-node-Pts_1_to_150000.txt.cleaned'
    filename_filtered = '../../emr_results/2-node-Pts_1_to_150000.txt.filtered'
    
    print "File :", filename
    level = 2
    file_name_2node = '../../emr_results/%d-node-Pts_1_to_150000.txt.frequent' % level
    frequent, counts = prune_two_size_episodes(filename, filename_filtered)
    print 'Writing to ', file_name_2node
    write_episodes_to_file(file_name_2node, frequent, counts)



''' Simultanous counts of all possible 2-node episodes '''
if __name__ == '__main__':
    #stream = emr_stream_reader('../../emrdata/Pts_1_to_150000.txt.cleaned')
    
    #stream = emr_all_data('../../emrdata')
    #outdir = '../../emr_results/'

    stream = emr_all_data2('../../emrdata2/nopx_stop_o')
    outdir = '../../emr_results2/'
    count_two_size_episodes(stream, outdir + '2-node-episodes_all.txt')
    
    
    
    
''' Count all 2-node episodes in all chunks'''
if __name__ == '__main__1':
    # Do it by parts
    flist = ['Pts_1_to_150000.txt.cleaned', 'Pts_150001_to_300000.txt.cleaned', 'Pts_300001_to_450000.txt.cleaned',\
     'Pts_450001_to_600000.txt.cleaned', 'Pts_600001_to_750000.txt.cleaned', 'Pts_750001_to_900000.txt.cleaned',\
     'Pts_900001_to_1050000.txt.cleaned', 'Pts_1050001_to_1200000.txt.cleaned', 'Pts_1200001_to_1350000.txt.cleaned',\
     'Pts_1350001_to_1500000.txt.cleaned', 'Pts_1500001_and_up.txt.cleaned', 'Extras.txt.cleaned']
    
    outdir = '../../emr_results/'
    for fname in flist:
        stream = emr_stream_reader('../../emrdata/%s' % fname)
        count_two_size_episodes(stream, outdir + '2-node-%s' % fname)
        print
        print
        

    
    