'''
Created on Dec 30, 2010

@author: patnaik
'''


class Vector(object):
    
    def __init__(self, initial_size = 10):
        self.internal_array = []
        
    def elementAt(self, index):
        return self.internal_array[index]

    def size(self):
        return len(self.internal_array)
    
    def contains(self, value):
        return value in self.internal_array
    
    def removeElement(self, value):
        self.internal_array.remove(value)
    
    def setElementAt(self, value, index):
        self.internal_array[index] = value
    
    def addElement(self, value):
        self.internal_array.append(value)
        
    def __len__(self):
        return len(self.internal_array)