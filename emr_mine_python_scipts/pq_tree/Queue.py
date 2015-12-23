'''
Created on Dec 30, 2010

@author: patnaik
'''

from collections import deque

class Queue(object):
    
    def __init__(self, data = None):
        if data:
            self.internal_queue = deque(data)
        else:
            self.internal_queue = deque()
        
    
    def enqueue(self, value):
        self.internal_queue.append(value)
        
    def dequeue(self):
        return self.internal_queue.popleft()
        
    def __len__(self):
        return len(self.internal_queue)
    
    def __str__(self):
        return "%s" % (list(self.internal_queue))