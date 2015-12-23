#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: ts=4 sts=4 sw=4 tw=79 sta et
"""%prog [options]
This module, supports reading and writing to a set of binary files representing
patient EMR records.
"""

__author__ = 'Patrick Butler'
__email__  = 'pbutler@killertux.org'

import struct
import os

RECSIZE = struct.calcsize("II")

def orderBy(a, b):
    o = cmp(a[1], b[1])
    if o == 0:
        return cmp(a[0], b[0])
    else:
        return 0

class RData(object):
    """ Reads binary data file representing EMR data
    """
    def __init__(self, dataname):
        """

        Parameters:
        dataname -- the files that that contain the binary data, minus their
        extensions
        """
        self.idx = open(dataname + ".idx", "rb")
        self.data = open(dataname + ".bin", "rb")
        self.nPats = os.path.getsize(dataname + ".idx") / RECSIZE

        emap = open(dataname + ".emap", "rb")
        self.map = []
        while True:
            n, = struct.unpack("i", emap.read( struct.calcsize("i") ))
            if n < 0: break
            self.map += [ emap.read(n) ]
        emap.close()

    def patients(self):
        for i in range(self.nPats):
            loc, nrecs = struct.unpack("II", self.idx.read(RECSIZE))
            yield i, nrecs ,self.records( ( loc, nrecs) )

    def records(self, patient):
        loc, nrecs = patient
        self.data.seek(loc)
        for i in range(nrecs):
            type, time = struct.unpack("II", self.data.read(RECSIZE))
            yield type, time

class WData(object):
    def __init__(self, dataname, order = False):
        self.idx = open(dataname + ".idx", "wb")
        self.data = open(dataname + ".bin", "wb")
        self.emap = open(dataname + ".emap", "wb")
        self.map = {}
        self.order = order
        self.dloc = 0

    def getIdx(self, label):
        if label not in self.map:
            self.map[label] = len(self.map)
        return self.map[label]

    def writePatient(self, records):
        if self.order:
            records.sort( lambda a,b: cmp( (a[1], a[0]), (b[1], b[0])))
        else:
            records.sort( lambda a,b: cmp( a[1], b[1] ))
        nrecs = len(records)
        self.idx.write( struct.pack("II", self.dloc, nrecs) )
        self.data.write( "".join([ struct.pack("II", *r) for r in records ]) )
        self.dloc += nrecs * RECSIZE

    def finish(self):
        mapvals = [ (idx, label) for label, idx in self.map.iteritems()]
        mapvals.sort()
        for idx, label in mapvals:
            #print idx, label
            self.emap.write( struct.pack("i", len(label)) + label)
        self.emap.write( struct.pack("i", -1))
        self.emap.close()
        self.idx.close()
        self.data.close()


def main(args):
    import  optparse
    parser = optparse.OptionParser()
    parser.usage = __doc__
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error("Not enough arguments given")
    if len(args) == 1:
        data = RData(args[0])
        for i in range(len(data.map)):
            print i, data.map[i]
        for i,n,p in data.patients():
            print "*", i, n
            for e,t in p:
                print t,e,data.map[e]
    elif len(args) == 2:
        data = RData(args[0])
        out = WData(args[1])
        for i,n,p in data.patients():
            records = [ (data.map[e], t) for e,t in p ]
            orecs = [ (out.getIdx(e), t) for e,t in records]
            out.writePatient(orecs)
        out.finish()
    return 0



if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )


