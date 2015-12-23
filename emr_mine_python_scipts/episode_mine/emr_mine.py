'''
Created on Dec 22, 2010

@author: patnaik
'''

from time import clock
from string import strip
from collections import defaultdict, deque
from struct import pack, unpack
from cPickle import load, dump


bad_records = 0



def emr_stream_reader(filename):
    global bad_records
    print 'Reading file:', filename
    for line in file(filename):
        try:
            parts = map(strip, line.split(","))
            (patient_id_str, med_code, med_type, t_day_str) = tuple(parts)
            patient_id = int(patient_id_str)
            t_day = int(t_day_str)
            if med_type == 'PX': continue
            if med_code == 'XXXXXX': continue
            yield (patient_id, med_code, med_type, t_day)
        except GeneratorExit:
            print "break exit"
        except:
            pass
            #print 'Error line:', line.strip()
            #bad_records += 1
            #raise
    print 'done'




def emr_all_data(path):
    flist = ['Pts_1_to_150000.txt.cleaned', 'Pts_150001_to_300000.txt.cleaned', 'Pts_300001_to_450000.txt.cleaned',\
     'Pts_450001_to_600000.txt.cleaned', 'Pts_600001_to_750000.txt.cleaned', 'Pts_750001_to_900000.txt.cleaned',\
     'Pts_900001_to_1050000.txt.cleaned', 'Pts_1050001_to_1200000.txt.cleaned', 'Pts_1200001_to_1350000.txt.cleaned',\
     'Pts_1350001_to_1500000.txt.cleaned', 'Pts_1500001_and_up.txt.cleaned'] #, 'Extras.txt.cleaned'
    
    emr_reader = emr_stream_reader_binary
    #emr_reader = emr_stream_reader
    
    #row_count = 0
    for f in flist:
        filename = path + '/%s' % f
        for record in emr_reader(filename):
            yield record
            #row_count += 1
            #if row_count > 1000: break
            

            
from emr import RData
def emr_all_data2(path):
    data = RData(path)
    for i,n,p in data.patients():
        #print "*", i, n
        for e,t in p:
            #print t,e,data.map[e]
            yield (i, data.map[e], 'DX', t)
            

def emr_data_filter(stream, eval_fun):
    patient_buffer = deque()
    flag = False
    prev_id = None
    for (patient_id, med_code, med_type, t_day) in stream:
        if patient_id != prev_id:
            #Clear the buffer
            if flag: #else skip the patient record
                for record in patient_buffer:
                    yield record
            flag = False
            patient_buffer.clear()
        
        if eval_fun(med_type, med_code): #encodes any operator
            flag = True
        
        patient_buffer.append((patient_id, med_code, med_type, t_day))
        prev_id = patient_id
        
    # Clean up the non-empty buffer
    if flag: #else skip the patient record
        for record in patient_buffer:
            yield record
                
        
        
    
def diabetes_filter(med_type, med_code):
    if med_code.startswith('250'): return True
    
    
    
def heart_filter(med_type, med_code):
    prefix = med_code[:3]
    if prefix in set(['425','426','427','428']): return True
    
    
def children_filter(med_type, med_code):
    prefix = med_code[:3]
    if prefix in set(['V03','V04','V05','V06']): return True
    
    
    
    

def generate_stats(stream):
    import pylab

    print "Reading EMR data..."
    patient_map = defaultdict(int)
    code_map = defaultdict(int)
    type_count = defaultdict(int)
    total_count = 0
    
    
    t1 = clock()
    for (patient_id, med_code, med_type, _) in stream:
        patient_map[patient_id] += 1
        code_map[med_code] += 1
        type_count[med_type] += 1
        total_count += 1
    t2 = clock()
    
    print "Time taken = %.2f sec" % (t2 - t1)
    print "Number of patients = %d" % len(patient_map)
    print "Number of codes = %d" % len(code_map)
    print "Number of Px/Dx codes PX = %d, DX = %d, EXP = %d" % (type_count['PX'], type_count['DX'], type_count['EXP'])
    print "Total number of records %d" % total_count
    print "Number of bad records = %d" % bad_records
    
    pylab.hist(patient_map.values(), bins = 100)
    pylab.title("Patient record distribution")
    pylab.xlabel("Number of records")
    pylab.ylabel("Freq")
    pylab.savefig("emr-patient-dist.png")
    
    pylab.hist(code_map.values(), bins = 100)
    pylab.title("Code distribution")
    pylab.xlabel("Number of records")
    pylab.ylabel("Freq")
    pylab.savefig("emr-codes-dist.png")

    
def emr_stream_reader_binary(filename, suffix = ".cleaned", infix = "-no-px"):
    suff_len = len(suffix)
    file_binary = filename[:-suff_len] + infix + ".binary"
    file_map = filename[:-suff_len] + infix + ".map"
    inv_code_map = load(open(file_map))
    inv_type_map = {0:'PX', 1:'DX', 2:'EXP'}
    print 'Reading file:', file_binary
    for line in file(file_binary):
        try:
            patient_id, med_code_int, med_type_int, t_day = unpack("IIII", strip(line))
            med_code = inv_code_map[med_code_int]
            med_type = inv_type_map[med_type_int]
            yield (patient_id, med_code, med_type, t_day)
        except GeneratorExit:
            print "break exit"
        except:
            pass
    print 'done'
    
''' Convert the dataset to binary '''
if __name__ == '__main__1':
    flist = ['Pts_1_to_150000.txt.cleaned', 'Pts_150001_to_300000.txt.cleaned', 'Pts_300001_to_450000.txt.cleaned',\
     'Pts_450001_to_600000.txt.cleaned', 'Pts_600001_to_750000.txt.cleaned', 'Pts_750001_to_900000.txt.cleaned',\
     'Pts_900001_to_1050000.txt.cleaned', 'Pts_1050001_to_1200000.txt.cleaned', 'Pts_1200001_to_1350000.txt.cleaned',\
     'Pts_1350001_to_1500000.txt.cleaned', 'Pts_1500001_and_up.txt.cleaned']

    suff_len = len('.cleaned')
    print flist[0][:-suff_len]
    type_map = {'PX':0, 'DX':1, 'EXP': 2}
    inv_type_map = {0:'PX', 1:'DX', 2:'EXP'}
    for f in flist:
        count = 0
        file_all = '../../emrdata/%s' % f
        file_binary = '../../emrdata/%s-no-px%s' % (f[:-suff_len], ".binary")
        file_map = '../../emrdata/%s-no-px%s' % (f[:-suff_len], ".map")
        code_map = {}; inv_code_map = {}; index = 0
        fout = open(file_binary, 'w')
        for (patient_id, med_code, med_type, t_day) in emr_stream_reader(file_all):
            if med_type == 'PX': continue
            if med_code == 'XXXXXX': continue
            
            #print (patient_id, med_code, med_type, t_day)
            if med_code not in code_map:
                code_map[med_code] = index
                inv_code_map[index] = med_code
                index += 1
            med_code_int = code_map[med_code]
            med_type_int = type_map[med_type]
            
            print >> fout, pack('IIII', patient_id, med_code_int, med_type_int, t_day)
            
#            count += 1
#            if count > 5: break
        fout.close()
        fout = open(file_map, 'w')
        dump(inv_code_map, fout, protocol=-1)
        fout.close()
        
'''    
(1, '441.4', 'DX', 0)
(1, '441.4', 'DX', 2)
(1, '441.4', 'DX', 933)
(1, '441.4', 'DX', 946)
(1, '573.2', 'DX', 946)
(1, '441.4', 'DX', 951)
(1, '441.4', 'DX', 1009)
(1, '401.9', 'DX', 1009)
(1, '424.0', 'DX', 1010)
(1, '414.00', 'DX', 1010)
(1, '518.3', 'DX', 1015)
'''
if __name__ == "__main__":
#    for (patient_id, med_code, med_type, t_day) in emr_all_data('../../emrdata'):
#        print (patient_id, med_code, med_type, t_day)
         
    generate_stats(emr_all_data('../../emrdata'))
    #generate_stats(emr_all_data2('../../emrdata2/nopx_stop_o'))
        
        
