'''
Created on Feb 16, 2011

@author: patnaik
'''
def print_incexc(n, symbols, m):
    pattern = [(n >> y) & 1 for y in range(m-1, -1, -1)]
    count = ' '.join(map(str, pattern)) + " & "
    pos = []; size = len(pattern) - sum(pattern)
    sign_map = {-1:"-", 1:"+"}
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
        count += "%sp(%s)" % (sign_map[sign], ''.join([symbols[i] for i in new_events]))
    count += r"\\"
    print count



if __name__ == "__main__":
    symbols = "ABC"
    m = 3
    for i in xrange(2**m):
        print_incexc(i, symbols, m)