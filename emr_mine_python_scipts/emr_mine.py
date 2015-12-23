'''
Created on Dec 22, 2010

@author: patnaik
'''

from time import clock
from string import strip
from collections import defaultdict
import pylab

bad_records = 0

def emr_stream_reader(filename):
    global bad_records
    print 'File:', filename
    for line in file(filename):
        try:
            parts = map(strip, line.split(","))
            (patient_id_str, med_code, med_type, t_day_str) = tuple(parts)
            patient_id = int(patient_id_str)
            t_day = int(t_day_str)
            yield (patient_id, med_code, med_type, t_day)
        except GeneratorExit:
            print "break exit"
        except:
            print 'Error line:', line.strip()
            bad_records += 1
            #raise

def emr_all_data(path): 
    flist = ['Pts_1_to_150000.txt.cleaned', 'Pts_150001_to_300000.txt.cleaned', 'Pts_300001_to_450000.txt.cleaned',\
     'Pts_450001_to_600000.txt.cleaned', 'Pts_600001_to_750000.txt.cleaned', 'Pts_750001_to_900000.txt.cleaned',\
     'Pts_900001_to_1050000.txt.cleaned', 'Pts_1050001_to_1200000.txt.cleaned', 'Pts_1200001_to_1350000.txt.cleaned',\
     'Pts_1350001_to_1500000.txt.cleaned', 'Pts_1500001_and_up.txt.cleaned', 'Extras.txt.cleaned']
    
    for f in flist:
        filename = path + '/%s' % f
        for record in emr_stream_reader(filename):
            yield record



def generate_stats(stream):
    print "Reading EMR data..."
    patient_map = defaultdict(int)
    code_map = defaultdict(int)
    type_count = defaultdict(int)
    total_count = 0
    
    
    t1 = clock()
    for (patient_id, med_code, med_type, t_day) in stream:
        patient_map[patient_id] += 1
        code_map[med_code] += 1
        type_count[med_type] += 1
        total_count += 1
    t2 = clock()
    
    print "Time taken = %.2f" % (t2 - t1)
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

    


if __name__ == '__main__':
    flist = ['Pts_1_to_150000.txt.cleaned', 'Pts_150001_to_300000.txt.cleaned', 'Pts_300001_to_450000.txt.cleaned',\
     'Pts_450001_to_600000.txt.cleaned', 'Pts_600001_to_750000.txt.cleaned', 'Pts_750001_to_900000.txt.cleaned',\
     'Pts_900001_to_1050000.txt.cleaned', 'Pts_1050001_to_1200000.txt.cleaned', 'Pts_1200001_to_1350000.txt.cleaned',\
     'Pts_1350001_to_1500000.txt.cleaned', 'Pts_1500001_and_up.txt.cleaned', 'Extras.txt.cleaned']
    
    generate_stats(emr_all_data('../emrdata'))
        
        
        
