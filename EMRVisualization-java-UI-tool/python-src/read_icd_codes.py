#! /usr/bin/python

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details:
# http://www.gnu.org/licenses/gpl.txt

__author__="debprakash"
__date__ ="$Dec 23, 2009 9:39:41 PM$"


from sgmllib import SGMLParser
from xml.sax.saxutils import quoteattr

                
class ICDParser(SGMLParser):
    def __init__(self, tags):
        verbose = 0
        SGMLParser.__init__(self, verbose)
        self.taglist = tags
        
    def reset(self):
        SGMLParser.reset(self)
        self.list = []
        self.inside_p_element = 0

    def start_p(self, attrs):
        self.class_content = None
        for (k, v) in attrs:
            if k == 'class':
                if v in self.taglist:
                    self.inside_p_element = 1
                    self.value = [v]
                    self.list.append(self.value)
                    self.flag = True
                else:
                    self.inside_p_element = 2
                    if self.flag:
                        self.value.append("")
                        self.flag = False

    def handle_data(self, data):
        if self.inside_p_element != 0:
            data = data.strip()
            if self.inside_p_element == 1:
                if len(data) > 0:
                    self.value.append(data)
            else:
                vlen = len(self.value)
                self.value[vlen-1] += data + " "


    def end_p(self):
        self.inside_p_element = 0



def convertToXML(filename):
    fin = open(filename + ".html")
    parser = ICDParser(['p1', 'p2', 'p6', 'p7','p9'])
    parser.feed(fin.read())

    xmlfile = open(filename + ".xml", "w")
    print >> xmlfile, "<?xml version=\"1.0\" encoding='UTF-8'?>"
    print >> xmlfile, "<root>"
    stack = []
    count = 0
    prev_level = -1
    desc = ""
    for tup in parser.list:
        if tup[0] == "p1":
            level = 0
            id, name = "", tup[1]
            if len(tup) > 2: desc = tup[2]
        elif tup[0] == "p2":
            if tup[1].endswith("."):
                level = 1
                id, name = "", tup[1] + tup[3]
                if len(tup) > 4: desc = tup[4]
            else:
                level = 2
                id, name = "", tup[1]
                if len(tup) > 2: desc = tup[2]
        elif tup[0] == "p6":
            level = 3
            id, name = tup[1], tup[2]
            if len(tup) > 3: desc = tup[3]
        elif tup[0] == "p7":
            level = 4
            id, name = tup[1], tup[2]
            if len(tup) > 3: desc = tup[3]
        elif tup[0] == "p9":
            level = 5
            id, name = tup[1], tup[2]
            if len(tup) > 3: desc = tup[3]


        while len(stack) > 0:
            (prev_level, endtag) = stack.pop()
            if prev_level >= level:
                print >> xmlfile, endtag
            else:
                stack.append((prev_level, endtag))
                break

        tab = "\t"
        for i in xrange(level): tab += "\t"
        tag = "<node id=%s name=%s desc=%s>" % (quoteattr(id), quoteattr(name), quoteattr(desc))
        print >> xmlfile, tab + tag
        stack.append((level, tab + "</node>"))

        count += 1
        if count > 10: break

    while len(stack) > 0:
        (prev_level, endtag) = stack.pop()
        print >> xmlfile, endtag
    print >> xmlfile, "</root>"

    xmlfile.close()

def convertToXML2(filename):
    fin = open(filename + ".html")
    parser = ICDParser(['p1', 'p2', 'p3', 'p6'])
    parser.feed(fin.read())

    xmlfile = open(filename + ".xml", "w")
    print >> xmlfile, "<?xml version=\"1.0\" encoding='UTF-8'?>"
    print >> xmlfile, "<root>"
    stack = []
    count = 0
    prev_level = -1
    desc = ""
    for tup in parser.list:
        #print tup
        if tup[0] == "p1":
            level = 0
            id, name = "", tup[1]
            if len(tup) > 2: desc = tup[2]
        elif tup[0] == "p2":
            level = 1
            id, name = "", tup[1] + tup[3]
            if len(tup) > 4: desc = tup[4]
        elif tup[0] == "p3":
            if tup[1].find(".") == -1:
                level = 2
                id, name = tup[1], tup[2]
                if len(tup) > 3: desc = tup[3]
            else:
                level = 3
                id, name = tup[1], tup[2]
                if len(tup) > 3: desc = tup[3]
        elif tup[0] == "p6":
            level = 4
            id, name = tup[1], tup[2]
            if len(tup) > 3: desc = tup[3]


        while len(stack) > 0:
            (prev_level, endtag) = stack.pop()
            if prev_level >= level:
                print >> xmlfile, endtag
            else:
                stack.append((prev_level, endtag))
                break

        tab = "\t"
        for i in xrange(level): tab += "\t"
        tag = "<node id=%s name=%s desc=%s>" % (quoteattr(id), quoteattr(name), quoteattr(desc))
        print >> xmlfile, tab + tag
        stack.append((level, tab + "</node>"))

        count += 1
        #if count > 10: break

    while len(stack) > 0:
        (prev_level, endtag) = stack.pop()
        print >> xmlfile, endtag
    print >> xmlfile, "</root>"

    xmlfile.close()

if __name__ == "__main__":
    #filename = "../Dtab10"
    #convertToXML(filename)
    filename = "../Ptab10"
    convertToXML2(filename)
    print "Done."
