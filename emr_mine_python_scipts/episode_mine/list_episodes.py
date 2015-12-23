'''
Created on Mar 14, 2011

@author: patnaik
'''

import csv

if __name__ == "__main__1":
    size = 7
    fin_name = "../../emr_results/all-data-lift-5/emr-episode-orderedset-%d.txt" % size
    fout_name = "../../emr_results/all-data-lift-5/parallel-episodes-%d.txt" % size
    
    fin = open(fin_name)
    fout = open(fout_name, "w")
    p_count = 0
    while True:
        line = fin.readline()
        if line == "": break
        
        parts = line.split(",")
        num = int(parts[1])
        count = int(parts[2])
        line = fin.readline().strip()
        pattern = ",".join(line.split(r"|"))
        print "%s:%d" % (pattern, count)
        print >> fout, "%s:%d" % (pattern, count)
        p_count += 1
        for _ in xrange(num):
            line = fin.readline()
    
    fin.close()
    fout.close()
    
    print p_count
    
    
if __name__ == "__main__":
    size = 3
    fin_name = "../../emr_results/all-data-lift-5/emr-episode-orderedset-%d.txt" % size
    fout_name = "../../emr_results/all-data-lift-5/serial-episodes-%d.txt" % size
    fout = open(fout_name, "w")
    
    #code_prefix = '250' #diabetes
    #code_prefix = '585' #chronic kidney disease
    #code_prefix = '571' #hepatitis
    #code_prefix = '191'
    
    code_list = ['008', '009', '038', '041', '057', '070', '112', '136', '141', '142', 
                 '144', '145', '146', '149', '150', '151', '153', '154', '155', '156', 
                 '157', '161', '162', '171', '172', '173', '174', '184', '188', '189', 
                 '191', '193', '194', '195', '196', '197', '198', '202', '204', '205', 
                 '208', '210', '211', '212', '214', '217', '218', '219', '220', '222', 
                 '223', '224', '225', '226', '227', '232', '233', '235', '236', '237', 
                 '238', '239', '240', '241', '242', '245', '246', '250', '252', '253', 
                 '256', '269', '272', '276', '280', '284', '285', '286', '287', '288', 
                 '289', '290', '291', '293', '294', '296', '300', '303', '305', '307', 
                 '310', '314', '327', '331', '336', '338', '342', '343', '344', '345', 
                 '348', '353', '355', '356', '357', '361', '362', '363', '364', '365', 
                 '366', '367', '368', '370', '371', '372', '374', '375', '376', '378', 
                 '379', '381', '382', '384', '385', '386', '388', '389', '394', '395', 
                 '396', '397', '401', '403', '410', '411', '412', '413', '414', '415', 
                 '421', '424', '425', '426', '427', '428', '429', '430', '431', '432', 
                 '433', '434', '435', '436', '437', '438', '440', '441', '442', '443', 
                 '444', '447', '451', '452', '453', '454', '455', '456', '458', '459', 
                 '461', '463', '464', '465', '466', '470', '471', '473', '474', '478', 
                 '482', '491', '492', '493', '494', '495', '496', '507', '511', '512', 
                 '514', '515', '516', '518', '519', '520', '528', '529', '530', '531', 
                 '532', '535', '536', '537', '540', '541', '543', '550', '552', '553', 
                 '555', '556', '560', '562', '564', '567', '568', '569', '570', '571', 
                 '572', '573', '574', '575', '576', '577', '578', '581', '583', '584', 
                 '585', '586', '590', '591', '592', '593', '596', '599', '600', '602', 
                 '603', '604', '605', '608', '610', '611', '614', '617', '618', '620', 
                 '621', '622', '624', '625', '626', '627', '628', '632', '634', '640', 
                 '641', '642', '644', '645', '646', '648', '650', '651', '652', '654', 
                 '655', '656', '658', '659', '661', '663', '664', '665', '667', '669', 
                 '675', '682', '686', '691', '700', '701', '702', '703', '706', '707', 
                 '708', '709', '714', '715', '716', '717', '718', '719', '721', '722', 
                 '723', '724', '726', '727', '728', '729', '730', '733', '737', '738', 
                 '739', '741', '742', '745', '746', '747', '748', '749', '752', '753', 
                 '754', '755', '756', '758', '762', '765', '769', '770', '771', '772', 
                 '774', '777', '779', '780', '781', '782', '783', '784', '785', '786', 
                 '787', '788', '789', '790', '791', '792', '793', '794', '795', '796', 
                 '799', '801', '802', '803', '805', '806', '807', '808', '811', '812', 
                 '813', '814', '815', '816', '817', '820', '821', '823', '824', '825', 
                 '826', '827', '829', '831', '832', '835', '836', '839', '840', '842', 
                 '844', '845', '850', '851', '852', '853', '854', '860', '861', '865', 
                 '867', '868', '869', '871', '879', '882', '883', '886', '891', '897', 
                 '901', '923', '924', '927', '939', '952', '958', '959', '963', '995', 
                 '996', '997', '998', '999', 'E812', 'E816', 'E819', 'E884', 'E888', 
                 'E915', 'E917', 'E918', 'E927', 'E950', 'V02', 'V03', 'V04', 'V05', 
                 'V06', 'V07', 'V10', 'V12', 'V15', 'V16', 'V17', 'V22', 'V23', 'V24', 
                 'V25', 'V26', 'V27', 'V28', 'V29', 'V30', 'V42', 'V43', 'V44', 'V45', 
                 'V46', 'V49', 'V50', 'V53', 'V54', 'V58', 'V59', 'V62', 'V65', 'V66', 
                 'V67', 'V71', 'V72', 'V76', 'V77', 'V80', 'V81']
    
    for code_prefix in code_list:
        count = 0; cover = 0; candidates = []
        fin = open(fin_name)
        while True:
            line = fin.readline() 
            if line == "": break
            #Parallel episode
            parts = line.split(",")
            num = int(parts[1]); pcount = int(parts[2])
            line = fin.readline().strip()
            pattern = ",".join(line.split(r"|"))
            #Serial episodes
            for _ in xrange(num):
                parts = fin.readline().split(":")
                episode = parts[0].split("|")
                scount = int(parts[1])
                rest_flag = any(map(lambda x:x.startswith(code_prefix), episode[:-1]))
                if (scount > 0.15 * pcount) and episode[-1].startswith(code_prefix) and not rest_flag:
                    #print "%s," % episode[:-1]
                    count += 1; cover += scount
                    candidates.append((episode, scount))
        
        print code_prefix, count, cover,
        if count > 10 and cover > 100:
            print 'ADDED'
            print >> fout, code_prefix, count, cover
            for (episode, scount) in candidates:
                print >> fout, "%s:%d" % ("->".join(episode), scount)
            for (episode, _) in candidates:
                print >> fout, "%s," % episode[:-1]
            print >> fout
        else:
            print
        fin.close()
    
    
    
    fout.close()
    
    
    
    
#List unique codes
if __name__ == "__main__1":
    size = 3
    fin_name = "../../emr_results/all-data-lift-5/emr-episode-orderedset-%d.txt" % size
    fout_name = "../../emr_results/all-data-lift-5/unique-endings-of-size-%d.txt" % size
    
    
    desc_map = {}
    fmap = csv.reader(open("../../emrdata/dxcodes.csv"))
    for line in fmap:
        print line
        break

    for line in fmap:
        #parts = line.strip().split(",")
        desc_map[line[0]] = " : ".join(line[1:]) 
    
    fin = open(fin_name)
    fout = open(fout_name, "w")
    p_count = 0
    unique_codes = set()
    while True:
        line = fin.readline()
        if line == "": break
        parts = line.split(",")
        num = int(parts[1])
        count = int(parts[2])
        line = fin.readline().strip()
        pattern = ",".join(line.split(r"|"))
        for _ in xrange(num):
            line = fin.readline()
            parts = line.split(":")
            episode = parts[0].split("|")
            scount = int(parts[1])
            last_event = episode[-1]
            if (scount > 0.1 * count) and last_event != 'XXXXXX':
                unique_codes.add(last_event)

    unique_codes = list(unique_codes)
    unique_codes.sort()
    for last_event in unique_codes:
        if last_event in desc_map:
            print >> fout, "%s:%s" % (last_event, desc_map[last_event])
            print "%s:%s" % (last_event, desc_map[last_event])
        else:
            print >> fout, "%s:%s" % (last_event, "-")
            print "%s:%s" % (last_event, "-")
        p_count += 1
    
    fin.close()
    fout.close()
    f = lambda code : code.split(".")[0]
    prefix_set = set([f(code) for code in unique_codes])
    prefix_set = list(prefix_set)
    prefix_set.sort()
    print p_count
    print prefix_set